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
    return out

from comparison_engine import MODES,prepare,transform

def load_series(spec,fetch_safe):
    kind,key,country,unit=spec
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
    left,right=st.columns([2,3])
    mode=left.segmented_control('표시 방식',MODES,default='표준화 · Z-score') or '원래 값'
    dates=right.date_input('비교 기간',(pd.Timestamp('2000-01-01').date(),data.now().date()),min_value=pd.Timestamp('2000-01-01').date(),max_value=data.now().date())
    if len(dates)!=2:st.info('시작일과 종료일을 선택해주세요.');return
    start,end=dates
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
            f=f[f.date.between(pd.Timestamp(start),pd.Timestamp(end))]
            if f.empty:st.warning(name+' · 선택 기간에 자료 없음');continue
            f['series']=name;frames.append(f);sources.append((name,unit,meta))
    if not frames:return
    combined=pd.concat(frames,ignore_index=True)
    combined=prepare(combined,start,end,frequency,aggregation,overlap)
    if combined.empty or (overlap and combined.series.nunique()!=len(frames)):
        st.info('공통 관측 기간이 없습니다. 공통 기간을 해제하거나 비교 대상을 변경해주세요.');return
    try:plot=transform(combined,mode)
    except ValueError as exc:st.info(str(exc));return
    units={name:u for name,u,_ in sources}
    normalized=mode in ('시작값 = 100','시작 대비 변화율 (%)','표준화 · Z-score')
    unit={'시작값 = 100':'기준값 100','시작 대비 변화율 (%)':'시작 대비 %','표준화 · Z-score':'표준편차'}.get(mode,'원단위')
    split=not normalized and len(set(units.values()))>1
    if split:
        st.caption('서로 다른 단위는 같은 날짜 축의 개별 그래프로 표시합니다. 겹쳐 보려면 표준화 또는 시작값 100을 선택하세요.')
        import altair as alt
        charts=[]
        for name,sub in plot.groupby('series',sort=False):
            charts.append(chart_ui.timeseries(sub,'date','value',units[name],height=180,domain=(start,end)).properties(title=name))
        st.altair_chart(alt.vconcat(*charts).resolve_scale(x='shared',y='independent'),use_container_width=True,theme=None)
    else:
        if not normalized:unit=next(iter(units.values()))
        st.altair_chart(chart_ui.timeseries(plot,'date','value',unit,group='series',height=420,domain=(start,end)),use_container_width=True,theme=None)
    with st.expander('단위 · 비교 기준 · 출처',expanded=False):
        st.caption('누락값은 보간하지 않습니다. 주기 통일은 실제 관측값의 마지막 값 또는 평균이며, 합계·전기비 자동 계산이 아닙니다. 월간 자료를 일간으로 늘리지 않습니다. 시작값 100은 각 계열의 구간 내 첫 관측값 기준이라 실제 기준일이 다를 수 있습니다. Z-score는 선택 기간 평균 0·표준편차 1로 환산하며 인과관계를 뜻하지 않습니다. 연간·월간 통계 날짜는 발표일이 아닙니다.')
        for name,u,meta in sources:st.markdown(f'[{name}]({meta.get("url", "https://fred.stlouisfed.org/")}) · {u}')
