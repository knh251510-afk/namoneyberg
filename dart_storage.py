"""Read public DART statement snapshots; credentials never enter saved payloads."""
from datetime import datetime
import json
from pathlib import Path
import re
import httpx
import streamlit as st

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'macro_cache'/'dart'
REPO='knh251510-afk/namoneyberg'
BRANCH='dart-data'


def filename(corp,year,basis):
    if not re.fullmatch(r'\d{8}',str(corp)) or basis not in ('CFS','OFS') or not 2015<=int(year)<=2100:
        raise ValueError('재무자료 조회 조건을 확인해주세요.')
    return f'{corp}_{int(year)}_{basis}.json'


def validate(payload,corp,year,basis):
    if not isinstance(payload,dict) or payload.get('corp_code')!=corp or payload.get('year')!=int(year) or payload.get('basis')!=basis:return None
    rows=payload.get('rows')
    if not isinstance(rows,list) or not rows or not all(isinstance(r,dict) for r in rows):return None
    if any(r.get('corp_code')!=corp or str(r.get('bsns_year'))!=str(year) or r.get('fs_div',basis)!=basis for r in rows):return None
    try:datetime.fromisoformat(payload['retrieved_at'])
    except (KeyError,ValueError,TypeError):return None
    return payload


def write_snapshot(folder,corp,year,basis,rows,retrieved_at):
    # Only official statement fields are published, never request parameters or URLs with keys.
    allowed={'rcept_no','reprt_code','bsns_year','corp_code','stock_code','fs_div','fs_nm','sj_div','sj_nm','account_id','account_nm','account_detail','thstrm_nm','thstrm_amount','thstrm_add_amount','frmtrm_nm','frmtrm_amount','frmtrm_q_nm','frmtrm_q_amount','frmtrm_add_amount','bfefrmtrm_nm','bfefrmtrm_amount','ord','currency'}
    clean=[{k:v for k,v in row.items() if k in allowed} for row in rows]
    payload={'corp_code':corp,'year':int(year),'basis':basis,'retrieved_at':retrieved_at,
             'source':'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json','rows':clean}
    if validate(payload,corp,year,basis) is None:raise ValueError('DART 재무자료 응답과 조회 조건이 다릅니다.')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    path=folder/filename(corp,year,basis)
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    temporary.replace(path)
    return payload


@st.cache_data(ttl=300,show_spinner=False,max_entries=512)
def read_snapshot(corp,year,basis,revision="20261019-five-companies"):
    name=filename(corp,year,basis)
    candidates=[]
    for folder in (ROOT/'static'/'dart-statements',CACHE):
        try:
            value=validate(json.loads((folder/name).read_text()),corp,year,basis)
            if value:candidates.append(value)
        except (OSError,ValueError,TypeError):pass
    try:
        response=httpx.get(f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/financials/{name}',timeout=httpx.Timeout(5,connect=2))
        if response.status_code==200:
            value=validate(response.json(),corp,year,basis)
            if value:candidates.append(value)
    except (httpx.HTTPError,ValueError):pass
    return max(candidates,key=lambda p:datetime.fromisoformat(p['retrieved_at']).timestamp()) if candidates else None


@st.cache_data(ttl=300,show_spinner=False)
def coverage():
    try:payload=json.loads((ROOT/'static'/'dart-coverage.json').read_text())
    except (OSError,ValueError):payload={'companies':[]}
    try:
        response=httpx.get(f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/coverage.json',timeout=httpx.Timeout(4,connect=2))
        if response.status_code==200:
            remote=response.json()
            if isinstance(remote,dict) and isinstance(remote.get('companies'),list):payload=remote
    except (httpx.HTTPError,ValueError):pass
    return [c for c in payload.get('companies',[]) if isinstance(c,dict) and re.fullmatch(r'\d{8}',str(c.get('corp_code',''))) and isinstance(c.get('years'),list)]


@st.cache_data(ttl=300,show_spinner=False)
def read_notices(corp):
    if not re.fullmatch(r'\d{8}',str(corp)):return None
    try:
        response=httpx.get(f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/notices/{corp}.json',timeout=httpx.Timeout(5,connect=2))
        if response.status_code==200:
            value=response.json()
            if isinstance(value,dict) and value.get('corp_code')==corp and isinstance(value.get('rows'),list):
                datetime.fromisoformat(value['retrieved_at'])
                return value
    except (httpx.HTTPError,ValueError,KeyError):pass
    return None
