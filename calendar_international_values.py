"""Only attach foreign actuals when country, definition and target month match."""
import pandas as pd
import streamlit as st
import macro_data as data

@st.cache_data(ttl=3600,show_spinner=False)
def cpi():
    return data.cpi_monthly()

def collect(frame,current):
    required=any(row['country']=='한국' and '소비자물가' in row['title'] and row['when']<current for _,row in frame.iterrows())
    if not required:return None
    try:return cpi()
    except Exception:return None

def values(row,loaded):
    if not loaded or row['country']!='한국' or '소비자물가' not in row['title']:return None
    frame,meta=loaded
    period=row.get('target_period')
    if not period:return None
    f=frame[frame.country=='KOR'].copy();f['month']=pd.to_datetime(f.date).dt.to_period('M')
    month=pd.Period(period,'M');current=f[f.month==month];prior=f[f.month==month-1]
    if current.empty:return None
    value=float(current.iloc[-1].value);previous=None if prior.empty else float(prior.iloc[-1].value)
    return {'name':'한국 CPI · 전년동월비','period':str(month),'value':value,'previous':previous,'change':None if previous is None else value-previous,'unit':'%','delta_unit':'%p','mom':None,'meta':meta,'url':meta.get('url','https://www.bis.org/statistics/cp.htm')}
