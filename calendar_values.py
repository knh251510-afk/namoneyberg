"""발표 대상월을 공식 시계열에 연결. 현재 DB 수정값이며 초도 발표값은 아님."""
import io,re,json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import streamlit as st
import macro_data as data

RULES=[('CPI','CPIAUCNS','CPI · 전년동월비','yoy'),('Consumer Price Index','CPIAUCNS','CPI · 전년동월비','yoy'),
('PPI','PPIFIS','PPI · 최종수요 전월비','mom'),('Producer Price Index','PPIFIS','PPI · 최종수요 전월비','mom'),
('PCE','PCEPI','PCE 물가 · 전월비','mom'),('Personal Income','PCEPI','PCE 물가 · 전월비','mom'),
('비농업','PAYEMS','비농업 고용 · 전월 증감','diff'),('Employment Situation','PAYEMS','비농업 고용 · 전월 증감','diff'),
('JOLTS','JTSJOL','JOLTS 구인 건수','level'),('Job Openings and Labor Turnover','JTSJOL','JOLTS 구인 건수','level'),
('무역수지','BOPGSTB','무역수지','level')]

def rule_for(title):return next((r for r in RULES if r[0] in title),None)

def target_month(row):
    match=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) (20\d{2})',row['title'])
    if match:return pd.Timestamp(datetime.strptime(match[0],'%B %Y'))
    # 날짜만 저장된 CPI 일정은 표준 익월 발표 대상월로만 연결.
    if row['title']=='CPI 소비자물가':return pd.Timestamp(row['when'].date()).replace(day=1)-pd.DateOffset(months=1)
    return None

@st.cache_data(ttl=3600,show_spinner=False)
def series(code):
    raw,meta=data.fetch(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}',3600)
    f=pd.read_csv(io.BytesIO(raw));f.columns=['date','value'];f['date']=pd.to_datetime(f.date);f['value']=pd.to_numeric(f.value,errors='coerce')
    return f.set_index('date').value.resample('MS').last(),meta

def saved_lookup():
    try:
        payload=json.loads(Path(__file__).with_name('calendar_cpi_results.json').read_text())
        frame=pd.DataFrame(payload['rows']);frame['date']=pd.to_datetime(frame.date)
        return {'_cpi_yoy':(frame,payload['meta'])}
    except (OSError,ValueError,KeyError):return {}

def collect(frame,current):
    codes={r[1] for _,row in frame.iterrows() if row['when']<current and (r:=rule_for(row['title'])) and target_month(row) is not None}
    def one(code):
        try:return code,series(code)
        except Exception:return code,None
    lookup=saved_lookup()
    with ThreadPoolExecutor(max_workers=4) as pool:lookup.update(dict(pool.map(one,codes)))
    if 'CPIAUCNS' in codes:
        try:lookup['_cpi_yoy']=data.cpi_monthly()
        except Exception:pass
    return lookup

def values(row,lookup):
    rule=rule_for(row['title']);month=target_month(row)
    if not rule or month is None:return None
    if rule[1]=='CPIAUCNS':
        direct=lookup.get(rule[1])
        if not direct or pd.isna(direct[0].get(month,float('nan'))):return cpi_fallback(month,lookup)
    if not lookup.get(rule[1]):return None
    raw,meta=lookup[rule[1]];mode=rule[3]
    transformed=(raw/raw.shift(12)-1)*100 if mode=='yoy' else ((raw/raw.shift(1)-1)*100 if mode=='mom' else (raw.diff() if mode=='diff' else raw))
    v=transformed.get(month);prev=transformed.get(month-pd.DateOffset(months=1))
    if v is None or pd.isna(v):return None
    change=None if prev is None or pd.isna(prev) else float(v-prev)
    unit='%' if mode in ('yoy','mom') else ('천 명' if rule[1] in ('PAYEMS','JTSJOL') else '백만 USD')
    # 물가지수는 수준의 전월 증가율, 비율 자체는 %p 차이를 표시.
    mom=(raw.get(month)/raw.get(month-pd.DateOffset(months=1))-1)*100 if raw.get(month-pd.DateOffset(months=1)) not in (None,0) else None
    return dict(name=rule[2],period=month.strftime('%Y.%m'),value=float(v),previous=prev,change=change,unit=unit,delta_unit='%p' if mode in ('yoy','mom') else unit,mom=mom,meta=meta,url=f'https://fred.stlouisfed.org/series/{rule[1]}')

def cpi_fallback(month,lookup):
    loaded=lookup.get('_cpi_yoy')
    if not loaded:return None
    frame,meta=loaded
    frame=frame[frame.country=='USA'].copy()
    frame['month']=pd.to_datetime(frame.date).dt.to_period('M')
    target=month.to_period('M');current=frame[frame.month==target];prior=frame[frame.month==target-1]
    if current.empty:return None
    value=float(current.iloc[-1].value);previous=None if prior.empty else float(prior.iloc[-1].value)
    return dict(name='CPI · 전년동월비',period=month.strftime('%Y.%m'),value=value,previous=previous,
        change=None if previous is None else value-previous,unit='%',delta_unit='%p',mom=None,meta=meta,
        url=meta.get('url','https://data.bis.org/topics/CPI'))
