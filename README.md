# My English Study

중급~고급 Business English 회의 대본을 학습하는 정적 웹사이트입니다.
영문 약 2,400단어(분당 120단어 기준 약 20분), 전체 한국어 번역,
12~20개 핵심 표현을 제공합니다. 루트와 business 페이지에서 날짜·주제·팀·표현을 검색합니다.

## 현재 구독으로 운영

ChatGPT에서 여러 날의 대본을 미리 작성해 `queue/business/YYYY-MM-DD.json`에 저장합니다.
GitHub Actions는 매일 한국 시간 06:30에 해당 날짜의 원본을 `data/business/`로 이동하고,
`business/YYYY-MM-DD {subject}.html` 및 목록을 생성·커밋한 뒤 GitHub Pages에 게시합니다.
API 키나 ChatGPT 로그인 정보는 저장소와 Actions에 넣지 않습니다.

미리 준비된 JSON은 공개 저장소에서 열람할 수 있습니다. 웹사이트 목록에는 게시일에만 나타납니다.
예약 실행은 GitHub 사정에 따라 늦어질 수 있습니다. 06:30 정각 게시 보장은 없습니다.
준비된 자료가 없으면 워크플로가 실패하고 기존 사이트는 유지됩니다.
게시 성공 후 해당 날짜의 링크를 포함한 GitHub Issue를 만들고 `bonjaykim`에게 할당합니다.
같은 날짜의 알림은 재실행해도 중복 생성하지 않습니다. 일반 코드 수정 배포에는 알림을 보내지 않습니다.
휴대폰의 GitHub 앱에서 같은 계정으로 로그인하고 **Profile → Settings → Notifications**에서
**Assignments** 알림을 켜 주세요. 휴대폰 OS에서도 GitHub 앱 알림을 허용해야 합니다.
Working Hours 또는 방해금지 모드가 06:30 알림을 차단하지 않는지 확인하세요.
푸시 수신은 GitHub와 휴대폰 설정에 따라 지연될 수 있습니다.
공개 저장소의 예약 워크플로는 60일간 활동이 없으면 비활성화될 수 있습니다.

## 최초 설정

1. 공개 GitHub 저장소의 기본 브랜치를 `main`으로 설정합니다.
2. Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 설정합니다.
3. Actions에서 최초 게시 결과를 확인합니다.
4. 예약된 날짜의 대본을 미리 채웁니다. Actions 수동 실행은 한국 날짜의 자료를 게시합니다.

## 새 학습 자료 준비

`prompts/daily-business.md`를 기준으로 기존 주제를 확인하고 날짜별 JSON을 작성합니다.
각 대본의 등장인물·수치·마감일·다음 회의 날짜와 번역을 검토합니다.
검증기는 형식·영문 분량·팀 수·번역 존재·표현 등장 여부를 확인합니다.
자연스러움과 번역의 정확성은 별도 내용 검토가 필요합니다.

```powershell
python scripts/check_queue.py
python scripts/build.py
python -m http.server 8000
```

`http://localhost:8000`에서 확인합니다. Python 3.12 이상을 사용하며 별도 라이브러리가 필요하지 않습니다.

## 구조

- `data/business/`: 게시된 원본 JSON
- `queue/business/`: 날짜별 게시 대기 원본 JSON
- `business/`: 요청한 파일명 형식의 게시된 HTML
- `scripts/build.py`: 검증 및 정적 페이지 생성
- `scripts/publish_due.py`: 한국 날짜 기준 중복 없는 게시
- `.github/workflows/pages.yml`: 예약 게시와 배포를 같은 실행에서 처리

배포에는 `dist/`의 HTML·CSS·JavaScript만 사용합니다. 원본, 대기 자료, 스크립트,
설정 파일은 Pages 배포 파일에 포함하지 않습니다.
다른 학습 분야는 category 검증과 렌더링을 확장한 후 폴더를 추가할 수 있습니다.
