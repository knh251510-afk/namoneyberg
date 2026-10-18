"""Session-preserving internal footer navigation."""
import streamlit as st

def render(pages):
    with st.container(key='footer_navigation'):
        brand,admin,sources=st.columns([8,1,1],vertical_alignment='center')
        brand.markdown('**NAMONEYBERG**')
        with admin:st.page_link(next(p for p in pages if p.url_path=='admin'),label='관리자')
        with sources:st.page_link(next(p for p in pages if p.url_path=='sources'),label='데이터 안내')
