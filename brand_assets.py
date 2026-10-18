"""Supplied wordmark and compact app icon."""
import base64
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).parent/'static'/'brand'

@st.cache_data(show_spinner=False)
def wordmark_uri(mode="light"):
    return 'data:image/webp;base64,'+base64.b64encode((ROOT/('namoneyberg-wordmark-dark.webp' if mode=='dark' else 'namoneyberg-wordmark.webp')).read_bytes()).decode()

def apply():
    from ui_theme import mode
    background="transparent" if mode()=="dark" else "#fff"
    st.markdown('''<style>
.st-key-brand_home a{width:190px!important;height:40px!important;min-height:40px!important;background:'''+background+''' url("'''+wordmark_uri(mode())+'''") center center/cover no-repeat!important;border-radius:4px;display:block!important;padding:0!important}
.st-key-brand_home a p{font-size:0!important;line-height:0!important}
.st-key-brand_home a:focus-visible{outline:2px solid var(--nb-accent);outline-offset:4px}
@media(max-width:800px){.st-key-brand_home a{width:160px!important;height:34px!important;min-height:34px!important}}
</style>''',unsafe_allow_html=True)
