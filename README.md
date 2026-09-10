# 수시 온도표 — 친구용 GitHub Pages 배포본

11개 지원 조합을 한 화면에서 비교하는 HTML 사이트입니다. 별도 Node.js 설치나 npm 빌드는 필요 없습니다. 배포는 본인의 GitHub 계정에서 진행합니다.

## 먼저 알아둘 현재 완성 범위

- 요청한 5개 대학, 11개 전형·학과 조합을 모두 등록했습니다.
- 2027학년도 현재 값은 **2026년 9월 10일 오전 10시 공식 발표**를 확인해 기본 자료로 넣었습니다. 배포 시 수집기가 새 발표를 확인합니다.
- 건국대·경희대의 2024~2026 최종 경쟁률, 이화여대의 2026 최종 경쟁률과 일부 이전 통합 전형 참고값을 포함했습니다.
- **과거 3개년 시간대별 곡선을 모두 확보한 버전은 아닙니다.** 확인된 최종값은 마감 지점의 점으로 표시합니다. 외대·시립대의 미확보 과거 자료는 빈 값으로 남겼습니다. 빈 값은 0 : 1이 아닙니다.
- 올해도 이미 지나간 발표 기록을 되살리는 기능은 아닙니다. 포함된 기본 자료와 배포 후 실제로 수집한 발표들을 누적하여 선을 만듭니다.
- 전형 구조가 다른 과거 자료는 ‘참고’ 조건을 표시합니다. 이화여대 2024·2025 미래인재전형은 올해 면접/서류형과 동일 전형으로 해석하면 안 됩니다.

## 1. 압축 풀고 화면 열기

ZIP 전체를 압축 해제합니다. `site/index.html`을 더블클릭하면 저장된 자료로 바로 사용할 수 있습니다. `index.html`, `style.css`, `app.js`, `data.js`를 같은 폴더에 유지하세요.

로컬에서 HTML을 여는 동안에는 원격 자동 수집이 실행되지 않습니다. GitHub 배포 후에는 컴퓨터를 꺼도 GitHub Actions가 동작합니다.

## 2. GitHub에서 빈 저장소 만들기

1. GitHub 로그인 → 오른쪽 위 **+ → New repository**.
2. Repository name: 예를 들어 `friend-admission-watch`.
3. GitHub Free로 Pages를 사용한다면 **Public**을 선택합니다. 공개 저장소에는 이 프로젝트 파일만 올리세요.
4. **Add a README file**, `.gitignore`, license 초기 생성은 선택하지 않습니다. 이미 파일을 제공하므로 빈 저장소를 만듭니다.
5. **Create repository**를 누릅니다.

이미 다른 프로젝트가 있는 저장소에 섞어 넣지 말고 별도 저장소를 사용하는 것이 간단합니다.

## 3. 로컬에서 최초 push

Git이 설치되어 있어야 합니다. 터미널에서 압축 해제한 프로젝트 폴더로 이동합니다. `README.md`, `sources.json`, `site`, `.github`가 있는 폴더가 기준입니다.

아래의 `YOUR_GITHUB_ID`와 저장소 이름을 자신의 것으로 바꾸세요. 폴더 경로도 실제 압축을 푼 위치를 사용합니다.

```bash
cd friend-admission-watch
git init
git branch -M main
git add .
git commit -m "Create admission competition dashboard"
git remote add origin https://github.com/YOUR_GITHUB_ID/friend-admission-watch.git
git push -u origin main
```

Git이 이름/이메일을 요청하면 이 저장소에서 아래를 한 번 실행하고 commit부터 다시 실행합니다.

```bash
git config user.name "YOUR_NAME"
git config user.email "YOUR_GITHUB_EMAIL"
```

HTTPS 로그인은 설치된 Git의 브라우저 로그인 또는 Git Credential Manager를 이용하세요. GitHub 계정 비밀번호를 터미널 비밀번호로 넣는 방식은 지원되지 않습니다. GitHub CLI를 이미 설치했다면 `gh auth login`으로 GitHub.com → HTTPS → 브라우저 로그인을 선택할 수도 있습니다. 비밀 토큰을 HTML이나 저장소에 넣을 필요는 없습니다.

macOS에서 `.github`가 Finder에 안 보이면 `Command + Shift + .`로 숨김 파일을 표시하세요. `git add .`는 `.github`도 포함합니다. 사이트 폴더만 올리면 자동 수집 설정이 빠집니다.

## 4. GitHub Pages 설정 — 반드시 한 번

1. 저장소 → **Settings → Pages**.
2. **Build and deployment → Source → GitHub Actions**를 선택합니다.
3. 저장소 상단 **Actions** 탭을 엽니다.
4. **Update competition and deploy Pages** 워크플로를 선택합니다.
5. **Run workflow → main → Run workflow**를 누릅니다. `include_history`는 처음에는 체크하지 않아도 됩니다.
6. 실행 내역의 `update`와 `deploy`가 모두 초록색이면 배포 완료입니다.
7. **Settings → Pages → Visit site** 또는 실행 내역의 `github-pages` 링크를 엽니다.

예상 주소 형식은 `https://YOUR_GITHUB_ID.github.io/friend-admission-watch/`입니다. 실제 표시된 주소를 친구에게 전달하세요. 저장소 주소와 사이트 주소는 다릅니다.

최초 push가 Pages 설정보다 먼저 실행되어 실패해도 정상적으로 복구할 수 있습니다. Pages의 Source를 GitHub Actions로 설정한 뒤 위 Run workflow를 실행하면 됩니다.

이 프로젝트는 **Deploy from a branch** 방식으로 설정하지 않습니다. 자동 수집의 커밋과 Pages 배포를 같은 워크플로에서 처리합니다. GitHub의 기본 자동화 토큰으로 만든 커밋이 또 다른 배포 작업을 시작할 것이라고 가정하지 않습니다.

## 5. 자동 업데이트는 어떻게 되나요?

1. GitHub Actions가 경쟁률 원문을 가져옵니다.
2. 학년도·대학·전형·학과·모집/지원 인원·경쟁률을 검증합니다.
3. 새 발표를 `site/data.json`에 추가하고 저장소에 커밋합니다. 같은 발표와 같은 값은 중복으로 쌓지 않습니다.
4. 같은 실행에서 사이트를 GitHub Pages에 배포합니다.
5. 친구의 화면은 60초마다 새 저장 자료가 있는지 확인합니다.

**수집 시도 간격은 15분**입니다. GitHub의 예약 실행은 지연되거나 누락될 수 있으므로 초 단위 실시간 보장은 아닙니다. 대학이 경쟁률을 하루 몇 번만 발표하면 그 사이에는 숫자가 그대로인 것이 정상입니다. 원문 발표 시각과 저장본 확인 시각을 구분하세요. 새로고침 버튼은 배포된 자료를 다시 불러오며, GitHub 수집기를 즉시 실행시키지는 않습니다.

수집 기간은 `sources.json`의 `collectFrom`~`collectUntil`, 기본 **2026-09-07~2026-09-14 한국 시간**입니다. 마감 후 최종 발표를 받을 여유 기간을 포함합니다. 이후에도 사이트는 계속 열리지만 자동 수집은 종료합니다. 다른 입시연도에는 대학별 원문 URL·학년도·마감일·학과/전형 명칭을 실제 모집요강과 대조하여 갱신해야 합니다. 연도 숫자만 바꾸면 안 됩니다.

수동으로 다시 수집하려면 **Actions → Run workflow**. 종료일 이후 재수집 또는 등록된 과거 최종 자료 갱신은 `include_history`를 체크합니다. 과거 자료를 갱신해도 없는 시간대별 이력이 자동 복원되지는 않습니다.

## 6. 나중에 화면을 수정하고 push하기

자동 수집기가 원격 저장소에 데이터 커밋을 만들기 때문에 수정 전에 최신 상태를 받으세요.

```bash
git pull --rebase origin main
# site/index.html 또는 site/style.css 등을 수정
git add .
git commit -m "Update dashboard"
git pull --rebase origin main
git push origin main
```

최초에 `-u`로 연결했으므로 이후 `git push origin`도 사용할 수 있습니다. `git push origin main`이 어느 브랜치를 올리는지 가장 명확합니다.

로컬 수정 사항이 있으면 먼저 commit한 뒤 pull하세요. 충돌이 나면 파일에서 충돌 내용을 확인하여 수정하고 `git add 해당파일` → `git rebase --continue`로 진행합니다. 취소하려면 `git rebase --abort`. 자동으로 쌓인 기록을 잃을 수 있으므로 강제 push는 사용하지 마세요.

## 7. 문제 해결

| 증상 | 확인할 곳 / 해결 |
|---|---|
| Pages 404 | Actions의 deploy 완료 여부, Settings → Pages의 Source가 GitHub Actions인지 확인. 완료 후 잠시 기다리고 저장소 이름까지 포함한 주소로 접속 |
| Actions가 안 보임 | 저장소 루트에 `.github/workflows/update-and-deploy.yml`이 올라갔는지 확인 |
| 자동화 실행 허용 안내 | 저장소 Actions 탭의 워크플로 활성화 안내를 확인 |
| `403` / permission denied로 데이터 push 실패 | Settings → Actions → General → Workflow permissions에서 저장소 쓰기 허용 여부 확인. 조직 정책/브랜치 보호가 막는 경우 그 저장소 정책에 맞춰 설정해야 함 |
| `configure-pages` 실패 | Settings → Pages → GitHub Actions를 선택하고 Run workflow 재실행 |
| 숫자가 그대로 | 원문 발표 시각, 대학의 발표 주기, Actions 실행 요약의 수집 성공 개수 확인 |
| 최근 수집 실패 표시 | 원문 점검/구조 변경/통신 실패 가능. 직전 자료는 보존됨. Actions의 Collect 단계 로그와 공식 원문을 확인 |
| 같은 날 오후에 멈춤 | 마감 전 경쟁률 공지가 중단될 수 있음. 마지막 공개 값을 최종값으로 바꾸지 않음 |
| `non-fast-forward` | 로컬 commit 후 `git pull --rebase origin main`을 실행하고 다시 push |
| 예약 실행이 오래 멈춤 | 수집 기간 및 Actions 활성화 확인. 공개 저장소는 활동이 없으면 예약 워크플로가 비활성화될 수 있음 |

## 8. 파일 구성과 로컬 검증

| 파일 | 역할 |
|---|---|
| `site/index.html` | 웹사이트 |
| `site/style.css` | 반응형 디자인 |
| `site/app.js` | 그래프·필터·CSV·자료 새로고침 |
| `site/data.json` | 프로그램 설정과 영구 수집 이력. 이 파일이 원본 |
| `site/data.js` | 파일 더블클릭 실행용 자료. 수집기가 JSON에서 자동 생성 |
| `sources.json` | 원문 URL·학년도·수집 기간·과거 전형 대응 |
| `scripts/collect.py` | Python 표준 라이브러리로 동작하는 수집기 |
| `.github/workflows/update-and-deploy.yml` | push/예약 수집과 Pages 배포 |
| `tests/` | 실제 공개 표 발췌에 대한 파서·중복 저장 검증 |

Python 3.11 이상이 있다면 아래 명령을 프로젝트 루트에서 실행할 수 있습니다. Windows에서 `python` 대신 `py`를 써야 할 수 있습니다.

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/collect.py --offline
python -m http.server 8000 --directory site
```

그다음 브라우저에서 `http://localhost:8000`을 엽니다. 종료는 Ctrl+C. 공식 원문을 실제로 다시 가져오려면 `python scripts/collect.py`, 등록된 과거 최종 자료까지 포함하려면 `python scripts/collect.py --history`를 사용합니다. 로컬 자료를 직접 수정한 뒤에는 `--offline`을 실행해 data.js도 맞추세요.

## 자료 신뢰성과 제한

공식 원문을 그대로 서비스하는 진학어플라이·유웨이 페이지를 사용합니다. 수시로가의 비공개 데이터나 내부 API를 복제하지 않습니다. 대학이 원문 주소나 표 구조를 변경하면 수집기 수정이 필요할 수 있습니다. 모든 수집 지점에 원문 링크를 기록하고, 자동 수집한 자료에는 원문 SHA-256 해시도 기록합니다. 통신 실패를 경쟁률 0으로 덮어쓰지 않습니다.

이 작업 환경에서는 GitHub 계정에 업로드하거나 실제 GitHub Actions를 실행하지 않았습니다. 공개 페이지의 값 확인과 로컬 파서 검증을 완료했으며, GitHub 실행 환경에서의 외부 통신·예약 실행·Pages 게시 성공은 위 첫 배포 후 실행 내역에서 확인해야 합니다.

## 공식 배포 참고

- [GitHub Pages 사용자 지정 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [GitHub Actions 예약 실행](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
