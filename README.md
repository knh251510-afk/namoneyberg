# NAMONEYBERG

경제 데이터, 시장 뉴스, 기업 재무자료를 한곳에서 살펴보는 Python·Streamlit 기반 리서치 웹서비스입니다.

**서비스:** [namoneyberg.streamlit.app](https://namoneyberg.streamlit.app/)

## 주요 기능

| 화면 | 제공 기능 |
| --- | --- |
| 마켓 오버뷰 | 매크로·글로벌·산업별 주간 브리핑, 출처 확인, 지난 게시본 조회 및 다운로드 |
| 뉴스 | 국내외 RSS 기사, 최근 주요 기사 요약, 상대 게시 시각 및 원문 링크 |
| 경제지표·시장 시세 | 국가별 거시지표와 시장 시계열 조회, 출처·단위·기준일 확인 |
| 국가 통계 | KOSIS 통계표 조회, 기간별 증감 및 최고·최저값 분석 |
| 데이터 비교 | 선택한 경제·시장 시계열의 수치와 추이 비교 |
| 기업 재무분석 | 기업 검색, 연간 연결·별도 재무자료, 다년 비교, Excel 추출 및 최근 공시 |
| 발표 일정 | 경제권·기간·중요도 필터, 발표값 및 정책회의 결정, 지표 설명 |
| 개념 지도 | 2D·3D 경제 개념 탐색, 노드 설명과 연결 관계 상호작용 |

홈 화면은 5개 기능 그룹의 이미지 카드로 구성되며, 페이지 간 이동과 라이트·다크 테마를 제공합니다. 브리핑 생성·편집·게시 및 API 설정은 관리자 기능입니다.

## 기술 구성

- **서버와 화면:** Python, Streamlit. 별도의 React 프런트엔드나 REST API 서버를 운영하는 구조는 아닙니다.
- **데이터 처리:** pandas, NumPy, requests/httpx, 작업군별 백그라운드 스레드 풀과 캐시.
- **시각화:** Plotly, Altair, HTML/CSS 및 JavaScript/Canvas 기반 개념 지도.
- **브리핑:** OpenAI API, LangGraph 실행 흐름, LangChain 검색 인터페이스.
- **뉴스 검색:** SQLite에 RSS 제목·요약을 보관하고 scikit-learn TF-IDF와 코사인 유사도로 검색합니다. 임베딩 기반 벡터 검색은 아닙니다.
- **파일과 운영:** openpyxl, JSON 스냅샷, GitHub Actions, Streamlit Community Cloud.

```text
공식 통계·시장 API / 뉴스 RSS
           ↓
Python 수집·정규화 → 로컬 캐시 / 뉴스 SQLite
           ↓
분석·차트·뉴스 검색 → Streamlit 화면

DART 수집기 → dart-data 브랜치 → 재무분석 화면
뉴스 검색 → 브리핑 초안 → 관리자 편집·게시 → briefing-data 브랜치
```

현재 브리핑 흐름은 색인 → 검색 → 경제 개념 문맥 연결 → 초안 생성 → 초안 정리입니다. 별도의 자동 AI 편집 검수나 숫자 일치 게이트는 현재 코드에 포함되지 않습니다. 게시 전 내용 판단은 관리자가 수행합니다.

## 로컬 실행

새 환경에는 Python 3.12를 권장합니다. 의존성은 `requirements.txt`와 여기서 포함하는 `requirements-rag.txt`에 지정되어 있습니다.

```bash
git clone https://github.com/knh251510-afk/namoneyberg.git
cd namoneyberg
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run dashboard.py
```

기본 접속 주소는 `http://localhost:8501`입니다. Windows에서는 가상환경 활성화에 `.venv\Scripts\activate`를 사용합니다. VS Code에서 같은 가상환경을 선택한 뒤 `python run_dashboard.py`로도 실행할 수 있습니다.

## API와 관리자 설정

API 키는 환경변수 또는 로컬 `.streamlit/secrets.toml`에 설정합니다. 배포 시에는 Streamlit Cloud의 앱 Secrets에 등록합니다. **키와 관리자 인증정보를 소스·JSON 데이터·커밋에 넣지 마세요.**

| 설정 이름 | 용도 | 필요한 경우 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 브리핑 초안·관련 이미지 생성 | 관리자 생성 기능 사용 |
| `ECOS_API_KEY` | 한국은행 통계 | ECOS 연결 지표 사용 |
| `KOSIS_API_KEY` | 국가 통계 | KOSIS 조회 |
| `DART_API_KEY` | 공식 기업 재무자료·공시 수집 | 신규 자료 수집 또는 직접 조회 |
| `NAMONEYBERG_ADMIN_HASH` | 관리자 로그인용 salt/hash JSON 문자열 | 관리자 기능 활성화 |
| `BRIEFING_GITHUB_TOKEN` | 게시본 저장소 Contents 쓰기 | 영구 게시 |
| `BRIEFING_GITHUB_REPO` | 게시본 저장소 `owner/name` | 기본값과 다른 저장소 사용 |
| `BRIEFING_GITHUB_BRANCH` | 게시본 브랜치 | 기본값 `briefing-data` 변경 |

예시 형식만 표시합니다. 사용하는 항목에 실제 값을 설정하세요.

```toml
KOSIS_API_KEY = "YOUR_KOSIS_KEY"
ECOS_API_KEY = "YOUR_ECOS_KEY"
DART_API_KEY = "YOUR_DART_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
BRIEFING_GITHUB_REPO = "knh251510-afk/namoneyberg"
BRIEFING_GITHUB_BRANCH = "briefing-data"
```

키 조회 우선순위는 **환경변수 → Streamlit Secrets → macOS Keychain**입니다. macOS의 기존 키체인 저장도 지원합니다. 브리핑 생성 모델은 관리자 API 설정에서 계정에 사용 가능한 모델로 지정하세요. 생성 및 이미지 요청에는 API 비용이 발생할 수 있습니다. 뉴스 화면의 RSS 요약 표시는 별도 LLM 생성과 구분됩니다.

관리자 인증에는 PBKDF2-SHA256 310,000회 해시, 상수시간 비교 및 8시간 세션 만료를 사용합니다. 재시도 제한은 세션 단위입니다. 배포용 관리자 해시 생성 방법은 [설정 가이드](docs/configuration.md)를 참고하세요.

## 데이터 저장 구조

| 위치 | 역할 | Git 관리 |
| --- | --- | --- |
| `main` | 앱 코드, 테스트, 실제 사용하는 정적 자산과 최소 대체 자료 | 유지 |
| `dart-data` 브랜치 | `financials/`, `notices/`, `coverage.json` | 수집 성공 자료만 게시 |
| `briefing-data` 브랜치 | `published_briefings/`의 공개 게시본 | 관리자 게시 |
| `macro_cache/` | 통계·시세 캐시, 뉴스 SQLite, 로컬 수집 결과 | 제외 |
| `macro_reports/` | 로컬 브리핑 및 편집 작업 자료 | 제외 |
| `published_briefings/` | 배포에 포함한 기존 게시본 대체 자료 | 유지 |
| `static/` 및 `calendar_*.json` | 기업 목록, 최소 재무자료, 일정 발표값, 화면 이미지 | 실행에 필요하여 유지 |

Streamlit 서버의 로컬 파일은 영구 저장소로 가정하지 않습니다. 브리핑 원격 게시는 대상 브랜치가 먼저 있어야 하며, 저장소 Contents 쓰기 권한을 가진 토큰이 필요합니다. 편집 이력은 공개 게시본에서 제외합니다. 자세한 내용은 [브리핑 저장](BRIEFING_STORAGE.md)을 참고하세요.

### DART 수집

배포 서버와 DART 사이의 직접 연결이 시간 초과될 수 있어, 앱은 저장된 재무자료를 우선 읽습니다. 기업 검색 목록과 실제 수집 완료 범위는 다릅니다. 제공 가능한 기업·연도는 데이터 브랜치의 `coverage.json` 및 화면 안내가 기준입니다.

2026-10-19 초기 복구 수집 범위는 **5개 기업 × 2020~2025년 × 연결·별도 = 60개 재무 스냅샷**, 기업별 최근 공시 최대 30건이었습니다. 이는 당시 수집 결과이며 실시간 갱신 보장은 아닙니다.

```bash
# DART_API_KEY가 환경변수에 설정된 수집 환경에서 실행
python scripts/collect_dart_financials.py \
  --companies 005930,000660,006400,005380,035420 \
  --year 2025 --span 5 \
  --output macro_cache/dart-published/financials
```

기존 Mac 키체인을 쓰는 환경에서는 `--use-keychain`을 추가할 수 있습니다. 출력 중 `financials/`, `notices/`, `coverage.json`만 데이터 브랜치에 게시합니다. 수집 실패 시 기존 정상 재무파일을 보존합니다.

GitHub Actions의 **Collect DART financial statements**도 수동 실행할 수 있습니다. 이 경로에는 **GitHub Actions Secrets**의 `DART_API_KEY`가 별도로 필요합니다. Streamlit Secrets와 Actions Secrets는 공유되지 않습니다. 현재 워크플로는 `workflow_dispatch` 방식이며 정기 실행 일정은 설정되어 있지 않습니다.

[DART 운영 및 장애 대응](docs/dart-operations.md) · [발표 일정 출처](CALENDAR_SOURCES.md)

## 주요 코드

```text
dashboard.py                 앱 진입점 및 페이지 연결
macro_data.py                거시지표·뉴스 수집
analysis_sources.py          분석용 데이터 소스와 DART 연결
statistics_ui.py             KOSIS 통계 화면
corporate_ui.py               기업 재무분석 화면
financial_model.py           재무모델링 표 및 계산
scripts/collect_dart_financials.py  재무·공시 수집기
dart_storage.py               저장 재무자료 조회 및 검증
news_retrieval.py             SQLite / TF-IDF 뉴스 검색
briefing_workflow.py          LangGraph 브리핑 실행 흐름
briefing_store.py             게시본 저장 및 동기화
economic_calendar.py          발표 일정 화면
concept_map.py / concept_space.py  개념 지도
landing_ui.py                 홈 탐색 카드
theme_tokens.py / assets/     테마와 스타일
test_*.py                     자동화 테스트
```

## 테스트

프로젝트 루트에서 실행합니다.

```bash
python -m unittest discover -p 'test_*.py'
```

주요 검증 대상은 주간 경계, 누락 자료, 출처 식별자, 저장 재무자료의 조회 조건 일치, 작업 풀 분리, 빈 선택 상태, 테마 및 뉴스 요약입니다. 자동화 테스트 통과가 외부 API의 현재 연결 상태나 실제 화면 품질을 모두 보장하지는 않습니다. 유료 API 생성과 배포 화면은 별도 확인이 필요합니다.

## 배포

Streamlit Community Cloud에서 이 저장소의 `main`, 진입 파일 `dashboard.py`를 지정하고 필요한 Secrets를 등록합니다. `.streamlit/config.toml`의 정적 파일 제공 설정은 이미지 표시를 위해 유지하세요. 앱 코드와 게시 데이터는 각각 `main`, `dart-data` / `briefing-data`로 분리합니다.

## 범위와 제약

- 통계의 관측일, 발표일, 수집일은 서로 다르며 국가별 정의·수정 여부도 다릅니다.
- 자료가 없는 값은 0으로 해석하지 않습니다. 저장 자료는 표시된 수집 시각을 확인해야 합니다.
- 뉴스 검색·브리핑은 RSS 제목과 제공 요약을 사용하며 유료 기사 원문 전체를 확보한 것으로 간주하지 않습니다.
- 자동 생성 초안의 수치·해석은 원문과 공식 통계로 확인한 뒤 게시해야 합니다.
- 모든 상장기업·연도·분기의 재무자료가 미리 수집되어 있는 것은 아닙니다. 현재 수집기는 연간 보고서 중심입니다.
- 사업보고서 문서 기반 자동 피어 선정·밸류에이션 RAG는 현재 제공 기능에 포함되지 않습니다.

## 자산과 라이선스

SEED CSS는 Apache-2.0이며 [원본 LICENSE와 NOTICE](assets/vendor/seed/package/)를 보존합니다. Pretendard 및 Tabler의 고지는 [licenses/](licenses/)에 있습니다. 프런트엔드는 SEED 토큰을 Streamlit에 적용한 어댑터이며 SEED React 컴포넌트를 직접 사용하는 구조는 아닙니다.

[브랜드 자산](docs/brand-assets.md) · [테마 이미지](docs/theme-artwork.md) · [디자인 토큰](DESIGN_SYSTEM.md)

이 저장소 전체에 대한 별도 오픈소스 라이선스는 아직 지정되어 있지 않습니다. 포함된 외부 라이브러리·자산·데이터의 이용조건은 각각 확인해야 합니다.
