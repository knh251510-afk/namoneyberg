"""SEED Design 3.0.3 token integration for Streamlit's native widgets.

Official CSS is vendored unchanged. This adapter is NAMONEYBERG code; it is
not the SEED React implementation and does not replace widget behavior.
"""
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).parent

def apply():
    base=(ROOT/'assets/vendor/seed/package/base.min.css').read_text()
    adapter=(ROOT/'assets/seed-streamlit.css').read_text()
    st.markdown('<style>'+base+'\n'+adapter+'</style>',unsafe_allow_html=True)
