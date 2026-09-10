import copy
import datetime as dt
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from collect import parse, merge, published_time

DATA=json.loads((ROOT/'site/data.json').read_text(encoding='utf-8'))
SOURCES=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))['sources']
NOW=dt.datetime(2026,9,10,12,tzinfo=dt.timezone(dt.timedelta(hours=9)))

class CollectorTests(unittest.TestCase):
    def parse_fixture(self,name,file=None):
        source=next(s for s in SOURCES if s['id']==name)
        programs=source.get('programs') or [p for p in DATA['programs'] if p['sourceId']==name]
        raw=(ROOT/'tests'/(file or (name+'.html'))).read_text(encoding='utf-8')
        return parse(raw,source,programs,NOW)

    def test_real_uway_tracks_and_aliases(self):
        rows,errors=self.parse_fixture('hufs')
        self.assertFalse(errors)
        self.assertEqual({r['programId']:r['ratio'] for r in rows},{'hufs-german-education':3.29,'hufs-politics-interview':7.88,'hufs-politics-document':5.29,'hufs-language-ai':5.5})
        self.assertTrue(all(r['publishedAt']=='2026-09-10T10:00:00+09:00' for r in rows))

    def test_final_publication_schedule_is_not_final(self):
        rows,errors=self.parse_fixture('uos')
        self.assertFalse(errors)
        self.assertEqual(rows[0]['applicants'],172)
        self.assertFalse(rows[0]['final'])

    def test_khu_campus_and_final(self):
        rows,errors=self.parse_fixture('khu','khu-current.html')
        self.assertFalse(errors)
        self.assertEqual(rows[0]['ratio'],5.98)
        rows,errors=self.parse_fixture('khu-2024','khu-final.html')
        self.assertFalse(errors)
        self.assertTrue(rows[0]['final'])
        self.assertEqual(rows[0]['ratio'],14.61)

    def test_jinhak_tracks(self):
        rows,errors=self.parse_fixture('ewha','ewha.html')
        self.assertFalse(errors)
        self.assertEqual({r['programId']:r['ratio'] for r in rows},{'ewha-office-interview':8.33,'ewha-office-document':5.83,'ewha-international':10.51,'ewha-german':7.77})

    def test_reject_wrong_year_and_missing_clock(self):
        source=next(s for s in SOURCES if s['id']=='hufs')
        raw=(ROOT/'tests/hufs.html').read_text(encoding='utf-8')
        with self.assertRaises(ValueError):parse(raw,{**source,'year':2030},[],NOW)
        self.assertIsNone(published_time('<p>원서접수 기간: 2026.09.08 ~ 2026.09.11</p>'))

    def test_ambiguous_department_never_guessed(self):
        source=next(s for s in SOURCES if s['id']=='khu')
        programs=[p for p in DATA['programs'] if p['sourceId']=='khu']
        raw=(ROOT/'tests/khu-current.html').read_text(encoding='utf-8')
        rows,errors=parse(raw+raw,source,programs,NOW)
        self.assertFalse(rows)
        self.assertIn('khu-international',errors)

    def test_history_retained_and_duplicate_rejected(self):
        original=copy.deepcopy(DATA['observations'][0]);history=[original]
        merge(history,[copy.deepcopy(original)],NOW.isoformat())
        self.assertEqual(len(history),1)
        new={**original,'publishedAt':'2026-09-10T14:00:00+09:00','applicants':100,'ratio':round(100/original['seats'],2)}
        merge(history,[new],NOW.isoformat())
        self.assertEqual(len(history),2)
        self.assertEqual(history[0]['applicants'],original['applicants'])
        merge(history,[{**original,'publishedAt':'2026-09-09T10:00:00+09:00'}],NOW.isoformat())
        self.assertEqual(len(history),2)

    def test_delivered_data_consistency(self):
        ids={p['id'] for p in DATA['programs']}
        self.assertEqual(len(ids),11)
        self.assertEqual(len({o['programId'] for o in DATA['observations'] if o['year']==2027}),11)
        for o in DATA['observations']:
            self.assertIn(o['programId'],ids)
            self.assertLessEqual(abs(o['applicants']/o['seats']-o['ratio']),.0051)
            self.assertTrue(o['sourceUrl'].startswith('https://'))

if __name__=='__main__':unittest.main()
