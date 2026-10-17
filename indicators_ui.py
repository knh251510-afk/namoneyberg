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
    name=st.selectbox('개별 지표',available,key='indicator_'+cat)
    if st.button('비교에 추가',key='add_indicator'):
        choices=list(st.session_state.get('comparison_selection',st.session_state.get('comparison_choices',[])))
        if name not in choices:choices.append(name)
        st.session_state['comparison_choices']=choices
        st.session_state['comparison_selection']=choices
        st.success('비교 목록에 추가했습니다.')
    st.markdown('[선택한 지표 조합하기 →](/compare)')
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
