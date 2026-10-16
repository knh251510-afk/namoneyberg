"""API 키는 Mac 키체인, 비밀이 아닌 설정은 로컬 JSON에 보관합니다."""
import json
from pathlib import Path
import os

SERVICES={'OpenAI':'research-agent-learning.openai','ECOS':'research-agent-learning.ecos',
          'DART':'research-agent-learning.dart'}
CONFIG=Path(__file__).resolve().parent/'app_preferences.json'


def read_key(name):
    env_name={'OpenAI':'OPENAI_API_KEY','ECOS':'ECOS_API_KEY','DART':'DART_API_KEY'}[name]
    value=os.environ.get(env_name)
    if value:return value
    try:
        import streamlit as st
        value=st.secrets.get(env_name)
        if value:return value
    except Exception:pass
    try:
        from keyring.backends.macOS import Keyring
        return Keyring().get_password(SERVICES[name],'api-key')
    except Exception:return None


def save_key(name,value):
    if not value.strip():return
    from keyring.backends.macOS import Keyring
    Keyring().set_password(SERVICES[name],'api-key',value.strip())


def model_name():
    try:return json.loads(CONFIG.read_text())['openai_model']
    except (OSError,ValueError,KeyError):return 'gpt-6-astra'


def save_model(value):
    CONFIG.write_text(json.dumps({'openai_model':value.strip() or 'gpt-6-astra'}))
