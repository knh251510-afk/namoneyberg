"""시장 시세와 스크롤 티커. 거래소 실시간 시세가 아닌 공급자 최신 관측값."""
from html import escape
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
import altair as alt
import streamlit as st
import macro_data as data
import chart_ui

SYMBOLS={'코스피':'^KS11','코스닥':'^KQ11','나스닥':'^IXIC','S&P 500':'^GSPC','다우':'^DJI',
'항셍':'^HSI','닛케이 225':'^N225','FTSE 100':'^FTSE','원/달러':'KRW=X',
'엔/달러':'JPY=X','위안/달러':'CNY=X','유로/달러':'EURUSD=X','비트코인':'BTC-USD','WTI 선물':'CL=F','금 선물':'GC=F'}

def direction(value):return 'rise' if value>0 else ('fall' if value<0 else 'flat')

@st.cache_data(ttl=300,show_spinner=False)
def quotes():
    import yfinance as yf
    def one(item):
        name,symbol=item;path=data.CACHE/('quote_'+symbol.replace('=','').replace('^','')+'.json')
        try:
            frame=yf.Ticker(symbol).history(period='5d',auto_adjust=False,timeout=10)
            close=frame.Close.dropna()
            if len(close)<2:raise ValueError('insufficient history')
            value,previous=float(close.iloc[-1]),float(close.iloc[-2])
            row={'name':name,'symbol':symbol,'value':value,'previous':previous,'change':value-previous,
                 'pct':(value/previous-1)*100,'date':close.index[-1].isoformat(),'fetched':data.now().isoformat(),'stale':False}
            data.CACHE.mkdir(exist_ok=True);path.write_text(json.dumps(row));return row
        except Exception:
            if path.exists():return {**json.loads(path.read_text()),'stale':True}
            return {'name':name,'symbol':symbol,'value':None,'stale':True}
    with ThreadPoolExecutor(max_workers=5) as pool:return list(pool.map(one,SYMBOLS.items()))

def tile(row):
    name=escape(row['name']);value=row['value']
    if value is None:return f'<div class="quote-item"><span>{name}</span><b>—</b><small>조회 불가</small></div>'
    decimals=4 if row['name'] in ('위안/달러','유로/달러') else 2
    change=row['change'];cls=direction(change);arrow='▲' if change>0 else ('▼' if change<0 else '−')
    return f'<div class="quote-item"><span>{name}</span><b>{value:,.{decimals}f}</b><strong class="{cls}">{arrow} {abs(change):,.{decimals}f} ({row["pct"]:+.2f}%)</strong><small>{escape(row["date"][:10])}'+(' · 저장값' if row['stale'] else '')+'</small></div>'

@st.fragment(run_every=300)
def ticker():
    rows=quotes();items=''.join(tile(r) for r in rows)
    st.markdown('<div class="quote-ticker" tabindex="0" aria-label="시장 시세. 마우스를 올리거나 키보드로 선택하면 이동이 멈춥니다."><div class="quote-track"><div class="quote-group">'+items+'</div><div class="quote-group" aria-hidden="true">'+items+'</div></div></div>',unsafe_allow_html=True)

@st.cache_data(ttl=300,show_spinner=False)
def history(symbol,period):
    import yfinance as yf
    frame=yf.Ticker(symbol).history(period=period,auto_adjust=False,timeout=15)
    if frame.empty:return pd.DataFrame()
    return pd.DataFrame({'일자':frame.index.tz_localize(None),'종가':frame.Close.values})

def render():
    st.subheader('글로벌 시장 시세')
    st.caption('지수 · 환율 · 원자재 · 디지털 자산 / 상승 빨강 · 하락 파랑 / 증감은 직전 거래일 종가 대비')
    if st.button('시세 새로고침'):
        quotes.clear();history.clear();st.rerun()
    rows=quotes()
    for title,names in [('주요 주가지수',list(SYMBOLS)[:8]),('환율',list(SYMBOLS)[8:12]),('원자재 · 디지털 자산',list(SYMBOLS)[12:])]:
        st.markdown('### '+title)
        st.markdown('<div class="quote-grid">'+''.join(tile(r) for r in rows if r['name'] in names)+'</div>',unsafe_allow_html=True)
    st.markdown('### 추이 살펴보기')
    name=st.segmented_control('시장',list(SYMBOLS),default='코스피',label_visibility='collapsed') or '코스피'
    period='max'
    chart_slot=st.container()
    try:
        frame=history(SYMBOLS[name],period)
        if not frame.empty:frame=frame[frame.일자.dt.year>=2000]
        if frame.empty:st.info('차트를 불러오지 못했습니다.')
        else:
            color='#d23847' if frame.종가.iloc[-1]>=frame.종가.iloc[0] else '#2766c5'
            chart_slot.altair_chart(chart_ui.timeseries(frame,'일자','종가',name,color=color,height=340),use_container_width=True,theme=None)
            high=frame.loc[frame.종가.idxmax()];low=frame.loc[frame.종가.idxmin()]
            left,right=st.columns(2)
            left.metric('기간 내 최고',f'{high.종가:,.4f}' if name in ('위안/달러','유로/달러') else f'{high.종가:,.2f}')
            left.caption(f'{high.일자:%Y-%m-%d}')
            right.metric('기간 내 최저',f'{low.종가:,.4f}' if name in ('위안/달러','유로/달러') else f'{low.종가:,.2f}')
            right.caption(f'{low.일자:%Y-%m-%d}')
    except Exception:st.info('시계열 조회에 실패했습니다. 잠시 후 새로고침해주세요.')
    with st.expander('시세 출처 · 기준 시각',expanded=False):
        st.caption('Yahoo Finance / yfinance. 장중에는 진행 중인 일봉 값이 포함될 수 있습니다. 휴장·시차 때문에 국가별 기준일이 다릅니다. 환율 상승은 표기된 통화쌍 가격의 상승을 뜻합니다.')
        for r in rows:
            st.caption(f'[{r["name"]}](https://finance.yahoo.com/quote/{r["symbol"]}/) · 관측 {r.get("date","없음")} · 조회 {r.get("fetched","없음")}'+(' · 연결 실패로 저장값 표시' if r['stale'] else ''))
