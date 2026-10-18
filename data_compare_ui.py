"""연결된 거시·시장 시계열 통합 비교."""
import pandas as pd
import streamlit as st
import macro_data as data
import market_ui
import chart_ui

def catalog():
    out={}
    for country,(name,_) in data.COUNTRIES.items():
        out[f'{name} / CPI · 전년동월비']=('cpi','',country,'%')
        out[f'{name} / 정책금리']=('policy','',country,'%')
        for key,(title,unit,_) in data.INDICATORS.items():out[f'{name} / {title} · 연간']=('wb',key,country,unit)
    for name,(_,unit,_) in data.FRED.items():out['고빈도 / '+name]=('fred',name,None,unit)
    out['유로존 / PPI · 전월비']=('euro_ppi','',None,'%')
    out['한국 / 경상수지 · 월간']=('ecos_current_account','',None,'십억 USD')
    out['일본 / 소비자 신뢰지수']=('jp_confidence','',None,'지수')
    for name,symbol in market_ui.SYMBOLS.items():
        unit='KRW/USD' if name=='원/달러' else ('JPY/USD' if name=='엔/달러' else ('CNY/USD' if name=='위안/달러' else ('USD/EUR' if name=='유로/달러' else ('USD' if name in ('WTI 선물','금 선물','비트코인') else '지수'))))
        out['시장 / '+name]=('market',symbol,None,unit)
    for name,item in st.session_state.get('external_series',{}).items():out[name]=('external',name,None,item['unit'])
    return out

from comparison_engine import prepare, with_baseline_changes

def load_series(spec,fetch_safe):
    kind,key,country,unit=spec
    if kind=='external':
        item=st.session_state.get('external_series',{}).get(key)
        return (item['frame'].copy(),item['meta'],None) if item else (pd.DataFrame(),{},'자료 없음')
    if kind=='market':
        try:
            f=market_ui.history(key,'max').rename(columns={'일자':'date','종가':'value'})
            meta={'url':f'https://finance.yahoo.com/quote/{key}/'};error=None
        except Exception:f=pd.DataFrame();meta={};error='조회 실패'
    elif kind=='ecos_current_account':
        import api_settings
        try:f,meta=data.korea_current_account(api_settings.read_key('ECOS') or '');error=None
        except Exception:f=pd.DataFrame();meta={};error='자료 없음'
    else:f,meta,error=fetch_safe(kind,key)
    if not error and not f.empty and country:f=f[f.country==country]
    return f,meta,error

def persist_selection():
    st.session_state['comparison_choices']=list(st.session_state.get('comparison_selection',[]))

def render(fetch_safe):
    st.subheader('통합 데이터 비교')
    options=catalog()
    selected=st.multiselect('비교할 데이터',list(options),default=st.session_state.get('comparison_choices',['미국 / CPI · 전년동월비','미국 / 정책금리']),key='comparison_selection',on_change=persist_selection,placeholder='국가·지표·지수·환율 검색')
    c1,c2,c3=st.columns([2,2,3])
    frequency=c1.selectbox('관측 주기',['원래 주기','월간','분기','연간'])
    aggregation=c2.selectbox('묶는 방식',['마지막 값','평균'],disabled=frequency=='원래 주기')
    overlap=c3.checkbox('공통 기간',True)
    if not selected:st.info('비교할 데이터를 선택해주세요.');return
    frames=[];sources=[]
    with st.spinner('선택한 데이터를 불러오고 있습니다…'):
        for name in selected:
            kind,key,country,unit=options[name]
            f,meta,error=load_series(options[name],fetch_safe)
            if error or f.empty:st.warning(name+' · 자료 없음');continue
            f=f[['date','value']].dropna().copy();f['date']=pd.to_datetime(f.date)
            if f.empty:st.warning(name+' · 선택 기간에 자료 없음');continue
            f['series']=name;frames.append(f);sources.append((name,unit,meta))
    if not frames:return
    combined=pd.concat(frames,ignore_index=True)
    first = max(pd.Timestamp('2000-01-01'), combined.date.min()).date()
    last = min(data.now().date(), combined.date.max().date())
    chart_area = st.container()
    if first == last:
        start = end = first
    else:
        start, end = st.slider('비교 기간 · 양 끝을 드래그해 조정', min_value=first, max_value=last,
                               value=(first, last), format='YYYY.MM.DD', key='comparison_range')
    combined=prepare(combined,start,end,frequency,aggregation,overlap)
    if combined.empty or (overlap and combined.series.nunique()!=len(frames)):
        st.info('공통 관측 기간이 없습니다. 공통 기간을 해제하거나 비교 대상을 변경해주세요.');return
    units={name:u for name,u,_ in sources}
    plot=with_baseline_changes(combined,units)
    with chart_area:
        st.caption('Y축은 실제 값입니다. 그래프에 커서를 올리면 시작 대비 차이와 변화율(%)을 함께 확인할 수 있습니다.')
        if len(set(units.values()))>1:
            st.caption('단위가 다른 데이터는 날짜 축을 맞춘 개별 그래프로 표시합니다.')
            import altair as alt
            charts=[]
            for name,sub in plot.groupby('series',sort=False):
                charts.append(chart_ui.timeseries(sub,'date','value',units[name],height=180,domain=(start,end)).properties(title=name))
            st.altair_chart(alt.vconcat(*charts).resolve_scale(x='shared',y='independent'),width='stretch',theme=None)
        else:
            st.altair_chart(chart_ui.timeseries(plot,'date','value',next(iter(units.values())),group='series',height=420,domain=(start,end)),width='stretch',theme=None)
    scales = plot.groupby('series').value.apply(lambda v: v.abs().median())
    positive_scales = scales[scales > 0]
    different_scale = len(set(units.values())) > 1 or (len(positive_scales) > 1 and positive_scales.max() / positive_scales.min() >= 20)
    if different_scale and plot.series.nunique() > 1:
        from comparison_engine import transform
        eligible = plot.groupby('series').value.first()
        names = eligible[eligible > 0].index
        if len(names) > 1:
            trend = transform(plot[plot.series.isin(names)], '시작값 = 100')
            st.markdown('#### 움직임 비교')
            st.caption('시작값 = 100 · 값의 규모가 다른 데이터의 상대적인 추이를 비교합니다.')
            st.altair_chart(chart_ui.timeseries(trend,'date','value','시작값 100',group='series',height=300,domain=(start,end)),width='stretch',theme=None)
        if len(names) < plot.series.nunique():
            st.caption('시작값이 0 이하인 데이터는 실제 값 그래프에서 확인해주세요.')
    with st.expander('단위 · 비교 기준 · 출처',expanded=False):
        st.caption('누락값은 보간하지 않습니다. 주기 통일은 실제 관측값의 마지막 값 또는 평균이며, 합계·전기비 자동 계산이 아닙니다. 월간 자료를 일간으로 늘리지 않습니다. 차이와 변화율은 각 계열의 선택 구간 첫 관측값 기준입니다. 금리 차이는 %p, 변화율은 %입니다. 시작값이 0 이하이면 변화율을 계산하지 않습니다. 연간·월간 통계 날짜는 발표일이 아닙니다.')
        for name,u,meta in sources:st.markdown(f'[{name}]({meta.get("url", "https://fred.stlouisfed.org/")}) · {u}')
