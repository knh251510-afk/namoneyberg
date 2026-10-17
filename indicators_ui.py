"""One catalog for browsing and composing economic/market series."""
from html import escape
import pandas as pd
import streamlit as st
import chart_ui
from data_compare_ui import catalog,load_series

CATEGORIES=['물가·금리','경기·무역','시장지표']
def category(name,spec):
    kind,key,_,_=spec
    if kind=='market':return '시장지표'
    if kind in ('cpi','policy','euro_ppi') or (kind=='wb' and key=='cpi'):return '물가·금리'
    if kind=='fred':
        if any(t in key for t in ['CPI','PPI','PCE','국채','금리차']):return '물가·금리'
        if any(t in key for t in ['실업','고용','산업생산','소매판매','주택']):return '경기·무역'
        return '시장지표'
    return '경기·무역'

def render(fetch_safe):
    options=catalog()
    cat=st.segmented_control('카테고리',CATEGORIES,default=st.session_state.pop('indicator_category',CATEGORIES[0]),key='indicator_category_choice') or CATEGORIES[0]
    available=[name for name,spec in options.items() if category(name,spec)==cat]
    left,right=st.columns([4,1],vertical_alignment='bottom')
    name=left.selectbox('살펴볼 지표',available,key='indicator_'+cat)
    def save_choices(choices):
        st.session_state['comparison_choices']=list(dict.fromkeys(choices))
        st.session_state['comparison_selection']=st.session_state['comparison_choices'][:]
    def add():
        save_choices(st.session_state.get('comparison_choices',[])+[name])
    choices=st.session_state.get('comparison_choices',[])
    right.button('선택 목록에 담기' if name not in choices else '선택됨',on_click=add,disabled=name in choices,use_container_width=True)
    with st.container(border=True,key='comparison_tray'):
        st.markdown('**함께 비교할 지표**')
        st.caption('다른 카테고리의 지표도 담을 수 있습니다. 목록에서 검색해 바로 추가하거나 ×로 제외하세요.')
        def update_tray():save_choices(st.session_state['indicator_comparison_tray'])
        # Refresh this widget from the persistent selection after adding another category.
        if st.session_state.get('indicator_comparison_tray')!=choices:
            st.session_state['indicator_comparison_tray']=choices[:]
        st.multiselect('선택 목록',list(options),key='indicator_comparison_tray',on_change=update_tray,placeholder='예: 미국 CPI + 한국 정책금리 + 코스피',label_visibility='collapsed')
        current=st.session_state.get('comparison_choices',[])
        c1,c2,c3=st.columns([3,2,1])
        c1.caption(f'{len(current)}개 선택' if current else '지표를 2개 이상 선택하면 비교할 수 있습니다.')
        def compare():st.session_state['open_comparison']=True
        c2.button(f'{len(current)}개 지표 비교하기',type='primary',disabled=len(current)<2,on_click=compare,use_container_width=True)
        def clear():save_choices([])
        c3.button('비우기',disabled=not current,on_click=clear,use_container_width=True)
    frame,meta,error=load_series(options[name],fetch_safe)
    if error or frame.empty:st.info('이 지표의 자료를 불러오지 못했습니다.');return
    f=frame[['date','value']].dropna().copy();f['date']=pd.to_datetime(f.date)
    f=f[f.date.between(pd.Timestamp('2000-01-01'),pd.Timestamp.now().normalize())].sort_values('date')
    if f.empty:st.info('표시할 관측값이 없습니다.');return
    st.subheader(name)
    last=f.iloc[-1];delta=None if len(f)<2 else float(last.value-f.value.iloc[-2])
    direction='rise' if delta is not None and delta>0 else ('fall' if delta is not None and delta<0 else 'flat')
    change='' if delta is None else f'<span class="{direction}">{delta:+.2f}</span>'
    st.markdown(f'<div style="display:flex;align-items:baseline;gap:16px;padding:12px 0 20px;font-variant-numeric:tabular-nums"><strong style="font-size:30px;font-weight:650;color:#234657">{last.value:,.2f}</strong><span style="font-size:12px;color:#596469">{escape(options[name][3])}</span>{change}</div>',unsafe_allow_html=True)
    st.altair_chart(chart_ui.timeseries(f,'date','value',options[name][3]),use_container_width=True,theme=None)
    with st.expander('기준 · 출처'):
        st.caption('마지막 관측: '+last.date.strftime('%Y-%m-%d')+' · 변화는 직전 관측값과의 차이')
        st.markdown('[원자료]('+meta.get('url','https://fred.stlouisfed.org/')+')')
