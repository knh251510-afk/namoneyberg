"""NAMONEYBERG 공통 디자인. 단일 스타일 정의로 레이아웃 충돌 방지."""
import streamlit as st
import altair as alt
PALETTE=['#23705f','#386cb0','#8761a6','#b07924','#b45270','#30858c','#74802d','#687887']
def apply():
    import seed_theme
    seed_theme.apply()
    def portal():
        return {'config':{'background':'#ffffff','font':'Pretendard','view':{'stroke':None},'range':{'category':PALETTE},'axis':{'labelColor':'#65716c','titleColor':'#46554e','gridColor':'#e8eeea','domainColor':'#becbc3','labelFont':'Pretendard','titleFont':'Pretendard'},'legend':{'labelColor':'#65716c','labelFont':'Pretendard','titleFont':'Pretendard'},'title':{'color':'#202927','font':'Pretendard'}}}
    alt.themes.register('macro_portal',portal)
    alt.themes.enable('macro_portal')
