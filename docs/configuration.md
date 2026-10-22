# 관리자 인증 설정

관리자 비밀번호 원문 대신 salt와 PBKDF2-SHA256 해시를 설정합니다. 아래 명령은 비밀번호를 터미널에 표시하지 않고 입력받습니다. 출력되는 JSON도 인증 설정이므로 공개 커밋에 넣지 마세요.

```bash
python - <<'PYTHON'
import getpass, hashlib, json, secrets
salt = secrets.token_hex(16)
password = getpass.getpass('관리자 비밀번호: ')
if not password:
    raise SystemExit('빈 비밀번호는 사용할 수 없습니다.')
value = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 310000).hex()
print(json.dumps({'salt': salt, 'hash': value}))
PYTHON
```

출력 JSON을 Streamlit Secrets에 TOML 리터럴 문자열로 등록합니다. 아래 값은 형식 예시이며 실제 출력으로 바꿔야 합니다.

```toml
NAMONEYBERG_ADMIN_HASH = '{"salt":"YOUR_SALT","hash":"YOUR_HASH"}'
```

환경변수 `NAMONEYBERG_ADMIN_HASH`로 같은 JSON 문자열을 전달해도 됩니다. `/admin`에서 로그인합니다. 로컬 Mac에는 `.private/` 아래 설정이 자동 생성될 수 있으며 이 폴더는 Git에서 제외합니다. 로그인 세션은 8시간이며 실패 후 재시도 간격은 세션 단위이므로 전체 사용자에 대한 중앙 제한으로 간주하지 않습니다.
