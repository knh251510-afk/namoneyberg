"""SEED Design 3.0.3 token integration for Streamlit's native widgets.

Official CSS is vendored unchanged. This adapter is NAMONEYBERG code; it is
not the SEED React implementation and does not replace widget behavior.
"""
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).parent

def apply():
    base=(ROOT/'assets/vendor/seed/package/base.min.css').read_text()
    selector=':root,:root[data-seed-color-mode=system][data-seed-user-color-scheme=light]'
    start=base.index('{',base.index(selector));end=base.index('}',start)
    light_tokens=':root'+base[start:end+1]
    app=(ROOT/'assets/app-theme.css').read_text()
    st.markdown('<style>'+base+'\n'+light_tokens+'\n'+app+'</style>',unsafe_allow_html=True)
