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

def _fetch_quotes():
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

def _saved_quotes():
    rows=[]
    for name,symbol in SYMBOLS.items():
        path=data.CACHE/('quote_'+symbol.replace('=','').replace('^','')+'.json')
        try:rows.append({**json.loads(path.read_text()),'stale':True})
        except (OSError,ValueError):rows.append({'name':name,'symbol':symbol,'value':None,'stale':True})
    return rows

def quotes():
    import quote_cache
    return quote_cache.request('market-quotes',_fetch_quotes,_saved_quotes,ttl=300)

def _clear_quotes():
    import quote_cache
    quote_cache.invalidate('market-quotes')
quotes.clear=_clear_quotes

def tile(row):
    name=escape(row['name']);value=row['value']
    if value is None:return f'<div class="quote-item"><span>{name}</span><b>—</b><small>조회 불가</small></div>'
    decimals=4 if row['name'] in ('위안/달러','유로/달러') else 2
    change=row['change'];cls=direction(change);arrow='▲' if change>0 else ('▼' if change<0 else '−')
    return f'<div class="quote-item"><span>{name}</span><b>{value:,.{decimals}f}</b><strong class="{cls}">{arrow} {abs(change):,.{decimals}f} ({row["pct"]:+.2f}%)</strong><small>{escape(row["date"][:10])}'+(' · 저장값' if row['stale'] else '')+'</small></div>'

@st.fragment(run_every=30)
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
    names=st.segmented_control('비교할 시장',list(SYMBOLS),selection_mode='multi',default=['코스피'],key='quote_trend_markets')
    st.caption('항목을 누르면 비교에 추가되고, 다시 누르면 제외됩니다.')
    if names:
        mode=st.radio('표시 기준',['시작값 100','원래 값'],horizontal=True,key='quote_trend_mode') if len(names)>1 else '원래 값'
        frames={}
        for name in names:
            try:
                f=history(SYMBOLS[name],'max').copy()
                if not f.empty:
                    f=f.dropna(subset=['일자','종가']).sort_values('일자')
                    f=f[(f.일자>=pd.Timestamp(2000,1,1)) & (f.일자<=pd.Timestamp.now())]
                if f.empty:st.warning(name+' 자료를 불러오지 못했습니다.')
                else:frames[name]=f
            except Exception:st.warning(name+' 시계열 조회에 실패했습니다.')
        if frames:
            start=max(f.일자.min() for f in frames.values());end=min(f.일자.max() for f in frames.values())
            if start>end:st.info('선택 항목들의 공통 조회 기간이 없습니다.')
            else:
                parts=[];summaries=[]
                for name,f in frames.items():
                    f=f[(f.일자>=start)&(f.일자<=end)].copy()
                    if f.empty:continue
                    high=f.loc[f.종가.idxmax()];low=f.loc[f.종가.idxmin()]
                    summaries.append({'시장':name,'최고값':high.종가,'최고일':high.일자.strftime('%Y-%m-%d'),'최저값':low.종가,'최저일':low.일자.strftime('%Y-%m-%d')})
                    f['시장']=name;f['원래 값']=f.종가
                    if mode=='시작값 100':
                        if f.종가.iloc[0]<=0:
                            st.warning(name+'의 시작값이 0 이하라 지수화에서 제외했습니다.');continue
                        f.종가=f.종가/f.종가.iloc[0]*100
                    parts.append(f)
                if parts:
                    if mode=='시작값 100':
                        st.altair_chart(chart_ui.timeseries(pd.concat(parts),'일자','종가','시작값 100',group='시장',height=380,domain=(start,end)),use_container_width=True,theme=None)
                        st.caption('공통 조회 구간의 각 시장 첫 유효값을 100으로 환산합니다. 휴장일은 보간하지 않아 시작 거래일이 다를 수 있습니다. 환율은 표시 통화쌍 기준이며 원화 환산 투자수익률이 아닙니다.')
                    else:
                        for f in parts:
                            name=f['시장'].iloc[0]
                            st.markdown('**'+name+'**')
                            st.altair_chart(chart_ui.timeseries(f,'일자','종가',name,height=260,domain=(start,end)),use_container_width=True,theme=None)
                    st.caption(f'공통 조회 구간 {start:%Y-%m-%d} ~ {end:%Y-%m-%d} · 아래 최고·최저는 원래 값 기준')
                    st.dataframe(pd.DataFrame(summaries),hide_index=True,use_container_width=True)
    else:st.info('비교할 시장을 하나 이상 선택해주세요.')
    with st.expander('시세 출처 · 기준 시각',expanded=False):
        st.caption('Yahoo Finance / yfinance. 장중에는 진행 중인 일봉 값이 포함될 수 있습니다. 휴장·시차 때문에 국가별 기준일이 다릅니다. 환율 상승은 표기된 통화쌍 가격의 상승을 뜻합니다.')
        for r in rows:
            st.caption(f'[{r["name"]}](https://finance.yahoo.com/quote/{r["symbol"]}/) · 관측 {r.get("date","없음")} · 조회 {r.get("fetched","없음")}'+(' · 연결 실패로 저장값 표시' if r['stale'] else ''))
