# My English Study

중급~고급 Business English 회의 대본을 학습하는 정적 웹사이트입니다.
영문 약 2,400단어(분당 120단어 기준 약 20분), 전체 한국어 번역,
12~20개 핵심 표현을 제공합니다. 루트와 business 페이지에서 날짜·주제·팀·표현을 검색합니다.

## System SW 트랙

시스템 소프트웨어 개발자 업무에 맞춘 회의 대본을 별도 트랙으로 제공합니다.
첫 화면의 **시스템 SW 회의 바로가기** 버튼이나 상단 메뉴의 **System SW**에서 `systemsw/index.html`로 바로 이동합니다.
`topic`에 아래 값을 쓰면 System SW 트랙으로 분류됩니다.

| topic | 주제 |
| --- | --- |
| `sw-kickoff` | 제품 개발 일정·킥오프 (개발 시작/마일스톤/완료 시점) |
| `sw-release` | 벤더사·Google 관계사와 BSP 및 OS 릴리스 일정 |
| `sw-debug` | system hang, lockup, kernel panic 등 시스템 이슈 원인 분석 (SQE·내부 개발·벤더·OS 업체) |
| `sw-status` | 버전 발행 후 문제점 현황 보고와 팀별 진행 상황 공유 |
| `sw-launch` | 출시 임박 긴급 이슈의 일정·원인 분석 점검 |
| `sw-field` | 출시 후 시장 이슈 보고와 대응 방안 |
| `sw-tech` | 개발자 기술 공유, 설계 토론, 프로세스 개선 |

`prompts/daily-system-sw.md`를 기준으로 작성하고, `python scripts/check_lessons.py <파일...>`로 개별 파일을 검증합니다.

## 현재 구독으로 운영

2026-10-13부터 ChatGPT 클라우드 예약을 매일(주말 포함) 한국 시간 06:40으로 설정했습니다.
실행할 때 전체 대본의 주제·요약과 최근 30편 본문을 확인해 새로운 System SW 회의를 작성합니다.
영문 2200~2800단어, 전체 한국어 번역, 실제 대본에서 인용한 표현을 검증한 후
`data/business/YYYY-MM-DD.json`을 main에 커밋합니다. push로 GitHub Actions가 HTML과
목록을 생성·배포하고, ChatGPT가 배포 성공 및 오늘 HTML을 확인한 후 링크 알림을 보냅니다.

06:40은 예약 기준 시각입니다. 현재 실행 모드가 유동적이므로 정각 시작은 보장되지 않으며,
대본 생성·배포·확인을 마친 뒤 알림이 도착합니다. PC를 켜 둘 필요는 없습니다.
2026-10-12 연결된 GitHub 기능의 실제 파일 쓰기 성공을 확인했습니다.
권한 오류가 재발하면 게시 완료로 알리지 않고 JSON 파일과 실패 원인을 알립니다.
API 키나 ChatGPT 로그인 정보를 저장소와 Actions에 넣지 않습니다.

대기열이 비어 실패하던 기존 06:30 GitHub 예약은 제거했습니다.
`queue/business` 게시 기능은 수동 workflow_dispatch로만 유지합니다.
수동 게시에서만 기존 GitHub Issue 알림을 사용하며, 일상 알림은 ChatGPT 예약이 담당합니다.

## 최초 설정

1. 공개 GitHub 저장소의 기본 브랜치를 `main`으로 설정합니다.
2. Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 설정합니다.
3. Actions에서 최초 게시 결과를 확인합니다.
4. 예약된 날짜의 대본을 미리 채웁니다. Actions 수동 실행은 한국 날짜의 자료를 게시합니다.

## 새 학습 자료 준비

홈에서는 8개 업무 주제, 게시 날짜 달력, 제목·팀·표현 검색을 함께 사용합니다.
JSON의 `topic`은 `strategy`, `sales`, `finance`, `people`, `operations`,
`marketing`, `projects`, `partnerships` 중 하나입니다. 기존 자료에서 생략하면
`projects`로 분류하며, 새 자료에는 명시합니다.

매일 신규 System SW 학습 자료는 `prompts/daily-system-sw.md`를 우선 적용합니다.

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
- `business/`: 요청한 파일명 형식의 게시된 HTML (두 트랙 공통)
- `systemsw/`: System SW 트랙 목록 페이지
- `scripts/build.py`: 검증 및 정적 페이지 생성
- `scripts/publish_due.py`: 한국 날짜 기준 중복 없는 게시
- `.github/workflows/pages.yml`: 예약 게시와 배포를 같은 실행에서 처리

배포에는 `dist/`의 HTML·CSS·JavaScript만 사용합니다. 원본, 대기 자료, 스크립트,
설정 파일은 Pages 배포 파일에 포함하지 않습니다.
다른 학습 분야는 category 검증과 렌더링을 확장한 후 폴더를 추가할 수 있습니다.
