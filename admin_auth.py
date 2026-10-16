"""관리자 인증. 세션별 인증과 만료, 미설정 시 접근 거부."""
import hashlib,hmac,json,os,secrets,sys,time
from pathlib import Path
import streamlit as st
PRIVATE=Path(__file__).resolve().parent/'.private'
HASH=PRIVATE/'admin_auth.json'

def digest(password,salt):return hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),310000).hex()

def configured_hash():
    value=os.environ.get('NAMONEYBERG_ADMIN_HASH')
    if not value:
        try:value=st.secrets.get('NAMONEYBERG_ADMIN_HASH')
        except Exception:pass
    if value:
        try:return json.loads(value)
        except (ValueError,TypeError):return None
    if HASH.exists():
        try:return json.loads(HASH.read_text())
        except (ValueError,OSError):return None
    return None

def provision_local():
    if sys.platform!='darwin' or configured_hash():return
    PRIVATE.mkdir(mode=0o700,exist_ok=True);os.chmod(PRIVATE,0o700)
    password=secrets.token_urlsafe(24);salt=secrets.token_hex(16)
    HASH.write_text(json.dumps({'salt':salt,'hash':digest(password,salt)}));os.chmod(HASH,0o600)
    file=PRIVATE/'admin-password.txt';file.write_text(password+'\n');os.chmod(file,0o600)

def is_admin():
    return bool(st.session_state.get('_admin_until',0)>time.time())

def require_admin():
    if is_admin():return True
    st.subheader('관리자 로그인')
    conf=configured_hash()
    if not conf:
        st.info('관리자 인증이 설정되지 않았습니다.');return False
    with st.form('admin_login',clear_on_submit=True):
        password=st.text_input('관리자 비밀번호',type='password')
        submitted=st.form_submit_button('로그인')
    if submitted:
        now=time.time()
        if now<st.session_state.get('_admin_retry',0):st.error('잠시 후 다시 시도해주세요.')
        else:
            st.session_state['_admin_retry']=now+3
            try:valid=hmac.compare_digest(digest(password,conf['salt']),conf['hash'])
            except (ValueError,KeyError,TypeError):valid=False
            if valid:
                st.session_state['_admin_until']=now+8*3600;st.rerun()
            else:st.error('비밀번호가 일치하지 않습니다.')
    return False

def logout():
    st.session_state.pop('_admin_until',None);st.rerun()
