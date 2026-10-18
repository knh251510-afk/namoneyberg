"""Shared app/chart themes, controlled without paid API calls."""
import streamlit as st
import altair as alt
from theme_tokens import colors,PALETTES
PALETTE=PALETTES['light']
def mode():return st.session_state.get('color_mode','light')
def toggle():
    st.session_state['color_mode']='dark' if mode()=='light' else 'light'
def control():
    dark=mode()=='dark'
    st.button('라이트' if dark else '다크',icon=':material/light_mode:' if dark else ':material/dark_mode:',help='화면과 이미지 시간대 전환',on_click=toggle,key='theme_toggle')
def apply():
    import seed_theme
    seed_theme.apply(mode())
    t=colors(mode())
    def portal():
        return {'config':{'background':t['bg'],'font':'Pretendard','view':{'stroke':None},'range':{'category':PALETTES[mode()]},'axis':{'labelColor':t['muted'],'titleColor':t['text'],'gridColor':t['grid'],'domainColor':t['border'],'labelFont':'Pretendard','titleFont':'Pretendard'},'legend':{'labelColor':t['muted'],'labelFont':'Pretendard','titleFont':'Pretendard'},'title':{'color':t['text'],'font':'Pretendard'}}}
    alt.themes.register('macro_portal',portal);alt.themes.enable('macro_portal')
