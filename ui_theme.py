"""NAMONEYBERG 공통 디자인. 단일 스타일 정의로 레이아웃 충돌 방지."""
import streamlit as st
import altair as alt
PALETTE=['#9cc5f0','#8cd8c1','#c1acf3','#e4be83','#e5a9bd','#80cad7','#b4c891','#b5bac9']
def apply():
    import seed_theme
    seed_theme.apply()
    def portal():
        return {'config':{'background':'#10151d','font':'Pretendard','view':{'stroke':None},'range':{'category':PALETTE},'axis':{'labelColor':'#a6b4c5','titleColor':'#c4d5e8','gridColor':'#283747','domainColor':'#405165','labelFont':'Pretendard','titleFont':'Pretendard'},'legend':{'labelColor':'#a6b4c5','labelFont':'Pretendard','titleFont':'Pretendard'},'title':{'color':'#e6edf5','font':'Pretendard'}}}
    alt.themes.register('macro_portal',portal)
    alt.themes.enable('macro_portal')
