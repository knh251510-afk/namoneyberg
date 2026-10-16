"""발표 대상월을 공식 시계열에 연결. 현재 DB 수정값이며 초도 발표값은 아님."""
import io,re
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

def collect(frame,current):
    codes={r[1] for _,row in frame.iterrows() if row['when']<current and (r:=rule_for(row['title'])) and target_month(row) is not None}
    def one(code):
        try:return code,series(code)
        except Exception:return code,None
    with ThreadPoolExecutor(max_workers=4) as pool:return dict(pool.map(one,codes))

def values(row,lookup):
    rule=rule_for(row['title']);month=target_month(row)
    if not rule or month is None or not lookup.get(rule[1]):return None
    raw,meta=lookup[rule[1]];mode=rule[3]
    transformed=(raw/raw.shift(12)-1)*100 if mode=='yoy' else ((raw/raw.shift(1)-1)*100 if mode=='mom' else (raw.diff() if mode=='diff' else raw))
    v=transformed.get(month);prev=transformed.get(month-pd.DateOffset(months=1))
    if v is None or pd.isna(v):return None
    change=None if prev is None or pd.isna(prev) else float(v-prev)
    unit='%' if mode in ('yoy','mom') else ('천 명' if rule[1] in ('PAYEMS','JTSJOL') else '백만 USD')
    # 물가지수는 수준의 전월 증가율, 비율 자체는 %p 차이를 표시.
    mom=(raw.get(month)/raw.get(month-pd.DateOffset(months=1))-1)*100 if raw.get(month-pd.DateOffset(months=1)) not in (None,0) else None
    return dict(name=rule[2],period=month.strftime('%Y.%m'),value=float(v),previous=prev,change=change,unit=unit,delta_unit='%p' if mode in ('yoy','mom') else unit,mom=mom,meta=meta,url=f'https://fred.stlouisfed.org/series/{rule[1]}')
