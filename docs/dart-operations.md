# DART 운영

## 현재 구조
- `static/dart-companies.json`: DART 공식 기업 검색에서 확인한 상장기업 고유번호. 네트워크 없이 기업을 찾습니다.
- `dart-data` 브랜치의 `financials/`: 수집에 성공한 연간 재무제표. 앱 코드 배포와 분리합니다.
- 앱은 저장 자료를 먼저 읽고 수집 시각을 표시합니다. 없는 연도만 DART 직접 조회를 시도합니다. 누락 연도는 0 대신 공란입니다.
- 앱에 포함한 최소 대체 자료는 삼성전자 2025년 연결 재무제표 한 건입니다. 원격 데이터 브랜치에는 2026-10-19에 5개 기업의 2020–2025년 연결·별도 자료를 게시했습니다. 실제 제공 범위는 `coverage.json`과 화면 안내를 확인하세요.

## 최초 설정 (관리자)
1. GitHub 저장소 Settings → Secrets and variables → Actions → New repository secret.
2. 이름 `DART_API_KEY`, 값은 기존 DART 인증키. 채팅이나 소스 파일에 입력하지 않습니다.
3. Actions → Collect DART financial statements → Run workflow.
4. 종목코드(쉼표 구분, 최대 30개), 마지막 연도, 비교 연수를 선택합니다. 연결·별도 둘 다 수집합니다.
5. 성공하면 `dart-data` 브랜치가 생깁니다. 사이트에서 같은 기업을 다시 조회하면 저장 자료를 읽습니다.

GitHub Actions도 DART에 연결되지 않으면 이 Mac처럼 연결을 확인한 환경에서 아래 수집기를 실행한 뒤 생성된 공개 재무자료만 `dart-data/financials`에 게시합니다. 인증키는 게시하지 않습니다.

```sh
python scripts/collect_dart_financials.py --companies 005930,000660 --year 2025 --span 3
```

기본 실행은 프로세스 환경변수 `DART_API_KEY`를 사용하며, 기존 로컬 키 설정을 읽으려면 `--use-keychain`을 지정합니다. 수집기는 키나 인증 URL을 출력하지 않습니다. 성공 파일만 교체하므로 시간 초과·요청 제한·자료 없음은 이전 성공 파일을 지우지 않습니다. 상태 010/011은 키 상태, 012는 IP, 020은 요청 제한을 확인합니다.

## 기업 목록 갱신
```sh
python scripts/refresh_dart_directory.py
```

공식 검색에서 KRX 상장기업 목록의 고유번호를 확인합니다. 미해결 종목은 JSON에 따로 기록합니다.

## 2026-10-19 복구 확인
Streamlit 서버는 DART의 TCP 연결이 30초 후에도 성립하지 않았습니다. 같은 날 기존 Mac의 원래 Python 3.9 환경에서는 키체인 키로 공식 API 호출에 성공했습니다. 이 경로로 삼성전자·SK하이닉스·삼성SDI·현대자동차·NAVER의 2020–2025년 연결/별도 재무제표 60건과 기업별 최근 공시 30건을 `dart-data` 브랜치에 게시했습니다. 따라서 현재 운영은 Streamlit 직접 연결 복구가 아니라 정상 연결되는 수집 환경과 웹 표시를 분리한 방식입니다.

로컬 기존 키를 쓰려면 원래 실행환경으로 아래 명령을 실행합니다. GitHub Secret 추가 등록은 필요 없습니다.

```sh
.venv/bin/python scripts/collect_dart_financials.py --use-keychain --companies 005930,000660,006400,005380,035420 --year 2025 --span 5 --output macro_cache/dart-published/financials
```

생성된 `financials/`, `notices/`, `coverage.json`만 데이터 브랜치에 게시합니다. 공식 기업자료 외의 설정·키·로그는 게시하지 않습니다. 미래 수집에서 없는 연도는 기존 성공 파일을 지우지 않습니다.
