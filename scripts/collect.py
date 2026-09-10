"""Fetch only explicitly configured public competition pages; keep audited observations.
Python 3.11+, standard library only. Never fabricates historical time points.
"""
from __future__ import annotations
import argparse, concurrent.futures, datetime as dt, hashlib, html, json, re, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
KST = dt.timezone(dt.timedelta(hours=9))
ALLOWED = {'addon.jinhakapply.com', 'ratio.uwayapply.com'}

def norm(s):
    return re.sub(r'\s+', '', html.unescape(s)).replace('Ⅰ','I').replace('Ⅱ','II').replace('ㆍ','·')

def clean(s):
    s = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', s, flags=re.S|re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', s))).strip()

def tables(raw):
    # Uway can place competition tables inside a layout table. Regex matching
    # <table>...</table> would swallow the nested tables and miss entire tracks.
    from html.parser import HTMLParser
    class TableReader(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack=[]; self.output=[]; self.heading=''; self.head=None
        def handle_starttag(self, tag, attrs):
            if re.fullmatch(r'h[1-6]',tag): self.head=[]
            if tag=='table': self.stack.append({'heading':self.heading,'caption':None,'rows':[],'row':None,'cell':None,'cap':False})
            if not self.stack:return
            t=self.stack[-1]
            if tag=='caption': t['caption']=[];t['cap']=True
            if tag=='tr':t['row']=[]
            if tag in ('td','th'):t['cell']=[]
            if tag=='br' and t['cell'] is not None:t['cell'].append(' ')
        def handle_data(self,value):
            if self.head is not None:self.head.append(value)
            if self.stack:
                t=self.stack[-1]
                if t['cap']:t['caption'].append(value)
                if t['cell'] is not None:t['cell'].append(value)
        def handle_endtag(self,tag):
            if re.fullmatch(r'h[1-6]',tag) and self.head is not None:
                self.heading=' '.join(''.join(self.head).split());self.head=None
            if not self.stack:return
            t=self.stack[-1]
            if tag=='caption':t['cap']=False
            if tag in ('td','th') and t['cell'] is not None:
                if t['row'] is not None:t['row'].append(' '.join(''.join(t['cell']).split()))
                t['cell']=None
            if tag=='tr' and t['row'] is not None:
                t['rows'].append(t['row']);t['row']=None
            if tag=='table':
                t=self.stack.pop();label=' '.join(''.join(t['caption'] or []).split())
                if not label or label in ('경쟁률 현황','경쟁률','모집단위별 경쟁률 현황'):label=t['heading']
                if t['rows']:self.output.append((label,t['rows']))
    reader=TableReader();reader.feed(raw);return reader.output

def published_time(raw):
    text = clean(raw)
    # Require date followed immediately by a clock, not the application date range.
    patterns = [r'(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\.?\s*(오전|오후)?\s*(\d{1,2}):(\d{2})\s*(?:현황|기준)',
                r'(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*(오전|오후)?\s*(\d{1,2})\s*[:시]\s*(\d{2})']
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            year, month, day, ampm, hour, minute = m.groups(); hour = int(hour)
            if ampm: hour = hour % 12 + (12 if ampm == '오후' else 0)
            return dt.datetime(int(year),int(month),int(day),hour,int(minute),tzinfo=KST).isoformat()
    return None

def parse(raw, source, programs, now=None):
    now = now or dt.datetime.now(KST)
    text = clean(raw)
    if not re.search(str(source['year'])+r'\s*학년도', text):
        raise ValueError('학년도 불일치 또는 원문 형식 변경')
    if source['universityCheck'] not in text and source['universityCheck'] not in raw:
        raise ValueError('대학명 검증 실패')
    timestamp = published_time(raw)
    # Do not misread "최종접수 마감 후" in an update schedule as a final announcement.
    final = bool(re.search(r'(?:최종\s*경쟁률\s*(?:현황|입니다)|최종\s*마감\s*현황|최종\s*지원\s*현황|최종\s*현황|최종\s*마감되었습니다|최종\s*마감\s*되었습니다)',text))
    if timestamp: final = False  # Scheduled future final publication is not a final result.
    if source.get('finalVerified'): final = True
    if timestamp and dt.datetime.fromisoformat(timestamp)>now+dt.timedelta(minutes=5):
        raise ValueError('미래 발표 시각: 저장 보류')
    if not timestamp and not final:
        raise ValueError('원문 발표 시각 미확인: 저장 보류')
    result, errors = [], {}
    all_tables = list(tables(raw))
    for p in programs:
        matches = []
        for heading, rr in all_tables:
            heading=norm(heading).removesuffix('경쟁률현황').removesuffix('경쟁률')
            if heading not in {norm(t) for t in p['sourceTracks']}: continue
            for row in rr:
                if not any(norm(c) in {norm(n) for n in p.get('sourceDepartments',[p['department']])} for c in row):continue
                for i,c in enumerate(row):
                    m = re.fullmatch(r'([\d,]+(?:\.\d+)?)\s*:\s*1', c)
                    if not m or i<2: continue
                    try:
                        seats, applicants = [int(v.replace(',','')) for v in row[i-2:i]]
                        ratio = float(m.group(1).replace(',',''))
                        if seats<=0 or applicants<0 or abs(applicants/seats-ratio)>.0051: continue
                    except ValueError: continue
                    matches.append(dict(programId=p['id'],year=source['year'],seats=seats,applicants=applicants,ratio=ratio,publishedAt=None if final else timestamp,final=final,sourceUrl=source['url'],sourceTrack=heading,deadline=p.get('deadline') if source['year']==2027 else source.get('deadline')))
        if len(matches)==1: result.extend(matches)
        else: errors[p['id']] = '전형·학과 일치 행 없음' if not matches else '동일 이름 행이 여러 개여서 저장 보류'
    return result, errors

def fetch(source):
    url=source['url']
    if urlparse(url).hostname not in ALLOWED: raise ValueError('허용된 공개 경쟁률 출처가 아님')
    req=Request(url,headers={'User-Agent':'AdmissionWatch/1.0 (public admission statistics)','Accept':'text/html'})
    with urlopen(req,timeout=25) as res:
        if urlparse(res.url).hostname not in ALLOWED: raise ValueError('예상하지 않은 원문 리디렉션')
        raw=res.read(5_000_001)
        if len(raw)>5_000_000:raise ValueError('원문 크기 초과')
        charset=res.headers.get_content_charset()
    candidates=[charset] if charset else []
    meta=re.search(br'charset\s*=\s*["\']?([\w-]+)',raw[:10000],re.I)
    if meta:candidates.append(meta.group(1).decode('ascii'))
    for encoding in candidates+['utf-8','cp949','euc-kr']:
        try:return raw.decode(encoding),hashlib.sha256(raw).hexdigest()
        except (UnicodeError,LookupError):pass
    raise ValueError('원문 문자 인코딩 오류')

def merge(observations, incoming, now):
    """Deduplicate source announcements; preserve revisions and reject time regressions."""
    for row in incoming:
        existing=[r for r in observations if r['programId']==row['programId'] and r['year']==row['year']]
        key=lambda r:(r.get('publishedAt'),r['final'],r['seats'],r['applicants'],r['ratio'])
        if any(key(r)==key(row) for r in existing):continue
        timed=[r['publishedAt'] for r in existing if r.get('publishedAt')]
        if not row['final'] and (any(r['final'] for r in existing) or (timed and row['publishedAt']<max(timed))):continue
        row['collectedAt']=now
        observations.append(row)
    return observations

def write_data(data):
    path=ROOT/'site/data.json'
    payload=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    tmp=path.with_suffix('.tmp');tmp.write_text(payload,encoding='utf-8');tmp.replace(path)
    (ROOT/'site/data.js').write_text('window.ADMISSION_DATA = '+payload.rstrip()+';\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');parser.add_argument('--history',action='store_true');args=parser.parse_args()
    data=json.loads((ROOT/'site/data.json').read_text(encoding='utf-8'))
    config=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    if args.offline:write_data(data);return
    now=dt.datetime.now(KST);stamp=now.isoformat(timespec='seconds');data['lastAttemptAt']=stamp
    sources=[s for s in config['sources'] if s.get('url') and (args.history or s['year']==2027)]
    # End automatic collection after the final publication grace period; manual --history is allowed.
    if now>dt.datetime.fromisoformat(config['collectUntil']) and not args.history:
        print('수집 기간 종료. 저장 자료를 배포합니다.');return
    success=0
    def work(s):
        raw,digest=fetch(s)
        ps=s.get('programs') or [p for p in data['programs'] if p['sourceId']==s['id']]
        incoming,errors=parse(raw,s,ps,now)
        for r in incoming:r['sourceHash']=digest
        return incoming,errors
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(work,s):s for s in sources}
        for job in concurrent.futures.as_completed(jobs):
            s=jobs[job]
            try:
                incoming,errors=job.result();merge(data['observations'],incoming,stamp)
                message='; '.join(f'{k}: {v}' for k,v in errors.items())
                data.setdefault('status',{})[s['id']]={'checkedAt':stamp,'error':message or None,'matched':len(incoming)}
                success+=len(incoming)
                print(f"{s['id']}: {len(incoming)}개 확인"+(f' / {message}' if message else ''))
            except Exception as exc:
                message=f'{type(exc).__name__}: {str(exc)[:180]}'
                data.setdefault('status',{})[s['id']]={'checkedAt':stamp,'error':message}
                print(f"::warning::{s['id']} — {message}")
    write_data(data)
    if not success:print('::warning::이번 수집에서 확인한 행이 없습니다. 기존 자료를 유지합니다.')
    if summary:=__import__('os').environ.get('GITHUB_STEP_SUMMARY'):
        Path(summary).write_text(f'## 경쟁률 수집\n\n{stamp}: {success}개 조합 확인.\n\n'+ '\n'.join(f"- {k}: {v.get('error') or '정상'}" for k,v in data.get('status',{}).items()),encoding='utf-8')

if __name__=='__main__': main()
