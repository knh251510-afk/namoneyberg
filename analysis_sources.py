"""KOSIS and OpenDART adapters. Never expose authenticated URLs in exceptions."""
import io,re,zipfile,math,json
from pathlib import Path
import xml.etree.ElementTree as ET
from html import unescape
import httpx
import pandas as pd
import streamlit as st

class SourceError(ValueError):pass

def request_json(base,params):
    try:
        r=httpx.get(base,params=params,timeout=httpx.Timeout(25,connect=5));r.raise_for_status();payload=r.json()
    except httpx.TimeoutException:raise SourceError('데이터 공급원의 응답이 지연되고 있습니다. 잠시 후 다시 조회해주세요.') from None
    except (httpx.HTTPError,ValueError):raise SourceError('데이터 공급원 연결에 실패했습니다. 인증·서비스 상태를 확인해주세요.') from None
    if isinstance(payload,dict):
        status=payload.get('status')
        if status and status!='000':
            if status=='013':return []
            raise SourceError(DART_ERRORS.get(status,'DART 응답 상태 '+str(status)))
        if payload.get('err') or payload.get('errCd'):raise SourceError('KOSIS 요청이 거절됐습니다. 키·통계표·분류 조건을 확인해주세요.')
    return payload

@st.cache_data(ttl=21600,show_spinner=False)
def kosis_search(query,_key):
    result=request_json('https://kosis.kr/openapi/statisticsSearch.do',{'method':'getList','apiKey':_key,'searchNm':query,'resultCount':20,'startCount':1,'sort':'RANK','format':'json','jsonVD':'Y'})
    if not isinstance(result,list):raise SourceError('KOSIS 검색 응답 형식을 확인할 수 없습니다.')
    return [r for r in result if r.get('ORG_ID') and r.get('TBL_ID')]

@st.cache_data(ttl=21600,show_spinner=False)
def kosis_rows(org,table,frequency,count,filters,_key):
    params={'method':'getList','apiKey':_key,'orgId':org,'tblId':table,'itmId':'ALL','objL1':'ALL','prdSe':frequency,'newEstPrdCnt':min(int(count),120),'format':'json','jsonVD':'Y'}
    params.update(filters)
    result=request_json('https://kosis.kr/openapi/Param/statisticsParameterData.do',params)
    if not isinstance(result,list):raise SourceError('KOSIS 자료 형식을 확인할 수 없습니다.')
    return result

def parse_kosis(rows):
    out=[]
    for r in rows:
        raw=str(r.get('DT','')).replace(',','').strip()
        try:value=float(raw)
        except ValueError:continue
        period=str(r.get('PRD_DE',''));freq=r.get('PRD_SE','')
        try:
            if freq=='Y' and re.fullmatch(r'\d{4}',period):date=pd.Timestamp(period+'-01-01')
            elif freq=='M' and re.fullmatch(r'\d{6}',period):date=pd.to_datetime(period,format='%Y%m')
            elif freq=='Q' and re.fullmatch(r'\d{6}',period):date=pd.Timestamp(int(period[:4]),(int(period[4:])-1)*3+1,1)
            else:continue
        except (ValueError,TypeError):continue
        dims=[str(r.get(f'C{i}','')) for i in range(1,9)]
        title=' / '.join([str(r.get('ITM_NM',''))]+[str(r[f'C{i}_NM']) for i in range(1,9) if r.get(f'C{i}_NM')])
        identity='|'.join([str(r.get('ORG_ID','')),str(r.get('TBL_ID','')),str(r.get('ITM_ID','')),str(r.get('UNIT_NM','')),freq]+dims)
        filters={'itmId':r.get('ITM_ID','')}
        filters.update({f'objL{i}':r.get(f'C{i}','') for i in range(1,9)})
        out.append({'date':date,'value':value,'series':identity,'label':title,'unit':r.get('UNIT_NM',''),'period':period,'filters':filters})
    return pd.DataFrame(out)

def summary(frame):
    f=frame[['date','value']].dropna().sort_values('date').drop_duplicates('date')
    if f.empty:return None
    last=f.iloc[-1];prev=f.iloc[-2] if len(f)>1 else None
    delta=None if prev is None else float(last.value-prev.value)
    pct=None if prev is None or prev.value<=0 else delta/prev.value*100
    return {'latest':float(last.value),'date':last.date,'previous':None if prev is None else float(prev.value),'delta':delta,'pct':pct,'high':f.loc[f.value.idxmax()].to_dict(),'low':f.loc[f.value.idxmin()].to_dict()}

DART_ERRORS={
 '010':'DART 인증키가 유효하지 않습니다. 관리자 API 설정을 확인해주세요.',
 '011':'DART 인증키를 사용할 수 없습니다. 키 사용 상태를 확인해주세요.',
 '012':'DART 허용 IP 설정과 공개 서버의 접속 IP를 확인해주세요.',
 '020':'DART 요청 한도를 초과했습니다. 잠시 후 다시 조회해주세요.',
 '800':'DART 서비스 점검 중입니다. 잠시 후 다시 조회해주세요.',
}

def parse_dart_companies(content):
    if not zipfile.is_zipfile(io.BytesIO(content)):
        try:
            response=ET.fromstring(content)
            status=response.findtext('status')
        except ET.ParseError:status=None
        raise SourceError(DART_ERRORS.get(status,'DART 기업 목록 응답 형식을 확인할 수 없습니다. 공급원 연결 상태를 확인해주세요.'))
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            name=next(n for n in z.namelist() if n.lower().endswith('.xml'))
            root=ET.fromstring(z.read(name))
    except (zipfile.BadZipFile,ET.ParseError,StopIteration):
        raise SourceError('DART 기업 목록 파일을 해석하지 못했습니다.') from None
    return [{'name':e.findtext('corp_name') or '', 'corp_code':e.findtext('corp_code'),'stock_code':e.findtext('stock_code')} for e in root.findall('list') if re.fullmatch(r'\d{6}',e.findtext('stock_code') or '')]

@st.cache_data(show_spinner=False)
def listed_companies():
    payload=json.loads(Path(__file__).with_name('static').joinpath('krx-companies.json').read_text())
    return sorted(payload['companies'],key=lambda c:c['name'].casefold())

def parse_dart_search(content):
    if 'corpTable' not in content:
        raise SourceError('DART 기업 검색 응답 형식을 확인하지 못했습니다.')
    matches=[]
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',content,re.S|re.I):
        company=re.search(r"select\('([0-9]{8})'\).*?>(.*?)</a>",row,re.S)
        stock=re.search(r'<td[^>]*>\s*([0-9A-Z]{6})\s*</td>',row,re.S|re.I)
        if company and stock:
            name=unescape(re.sub(r'<[^>]+>','',company.group(2))).strip()
            matches.append({'name':name,'corp_code':company.group(1),'stock_code':stock.group(1)})
    return matches

@st.cache_data(ttl=86400,show_spinner=False,max_entries=512)
def dart_search(query,_key):
    query=query.strip()
    if not query:return []
    try:
        response=httpx.post('https://dart.fss.or.kr/dsae001/search.ax',
            data={'textCrpNm':query,'currentPage':'1','maxResults':'100'},
            timeout=httpx.Timeout(12,connect=5))
        response.raise_for_status()
        return parse_dart_search(response.text)
    except (httpx.HTTPError,SourceError):
        # Official API directory is a fallback if the public search changes.
        companies=dart_companies(_key)
        return [c for c in companies if query.casefold() in c['name'].casefold() or query in c['stock_code']][:100]

@st.cache_data(ttl=86400,show_spinner=False)
def dart_companies(_key):
    try:
        r=httpx.get('https://opendart.fss.or.kr/api/corpCode.xml',params={'crtfc_key':_key},timeout=httpx.Timeout(8,connect=3));r.raise_for_status()
    except httpx.TimeoutException:raise SourceError('DART 기업 목록 응답이 지연되고 있습니다. 다시 검색해주세요.') from None
    except httpx.HTTPError:raise SourceError('DART 기업 목록 서버에 연결하지 못했습니다. 공급원 상태를 확인해주세요.') from None
    return parse_dart_companies(r.content)

@st.cache_data(ttl=86400,show_spinner=False,max_entries=1024)
def resolve_dart_company(stock_code, key):
    """Use the small public search response before downloading the full directory."""
    try:
        response=httpx.post('https://dart.fss.or.kr/dsae001/search.ax',
            data={'textCrpNm':stock_code,'currentPage':'1','maxResults':'100'},
            timeout=httpx.Timeout(8,connect=3))
        response.raise_for_status()
        company=next((c for c in parse_dart_search(response.text) if c['stock_code']==stock_code),None)
        if company:return company
    except (httpx.HTTPError,SourceError):pass
    company = next((c for c in dart_companies(key) if c['stock_code'] == stock_code), None)
    if company is None:
        raise SourceError('DART에서 선택한 기업의 고유번호를 찾지 못했습니다.')
    return company

@st.cache_data(ttl=21600,show_spinner=False)
def dart_statement(corp,year,basis,_key):
    result=request_json('https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json',{'crtfc_key':_key,'corp_code':corp,'bsns_year':year,'reprt_code':'11011','fs_div':basis})
    return result.get('list',[]) if isinstance(result,dict) else []

@st.cache_data(ttl=3600,show_spinner=False)
def dart_disclosures(corp,start,end,_key):
    result=request_json('https://opendart.fss.or.kr/api/list.json',{'crtfc_key':_key,'corp_code':corp,'bgn_de':start,'end_de':end,'page_count':30,'page_no':1,'sort':'date','sort_mth':'desc'})
    return result.get('list',[]) if isinstance(result,dict) else []

ACCOUNTS={
 '매출액':(['ifrs-full_Revenue','ifrs_Revenue'],['매출액','수익(매출액)','영업수익'],['IS','CIS']),
 '영업이익':(['dart_OperatingIncomeLoss'],['영업이익','영업이익(손실)'],['IS','CIS']),
 '순이익':(['ifrs-full_ProfitLoss','ifrs_ProfitLoss'],['당기순이익','당기순이익(손실)'],['IS','CIS']),
 '자산':(['ifrs-full_Assets','ifrs_Assets'],['자산총계'],['BS']),
 '부채':(['ifrs-full_Liabilities','ifrs_Liabilities'],['부채총계'],['BS']),
 '자본':(['ifrs-full_Equity','ifrs_Equity'],['자본총계'],['BS']),
 '영업현금흐름':(['ifrs-full_CashFlowsFromUsedInOperatingActivities'],['영업활동현금흐름','영업활동으로인한현금흐름'],['CF'])}

ACCOUNTS.update({
 '매출원가':(['ifrs-full_CostOfSales'],['매출원가'],['IS','CIS']),
 '매출총이익':(['ifrs-full_GrossProfit'],['매출총이익'],['IS','CIS']),
 '판매관리비':(['dart_TotalSellingGeneralAdministrativeExpenses'],['판매비와관리비','판매비및관리비'],['IS','CIS']),
 '법인세차감전이익':(['ifrs-full_ProfitLossBeforeTax'],['법인세비용차감전순이익','법인세비용차감전순이익(손실)'],['IS','CIS']),
 '법인세비용':(['ifrs-full_IncomeTaxExpenseContinuingOperations'],['법인세비용'],['IS','CIS']),
 '유동자산':(['ifrs-full_CurrentAssets'],['유동자산'],['BS']),
 '현금및현금성자산':(['ifrs-full_CashAndCashEquivalents'],['현금및현금성자산'],['BS']),
 '재고자산':(['ifrs-full_Inventories'],['재고자산'],['BS']),
 '유형자산':(['ifrs-full_PropertyPlantAndEquipment'],['유형자산'],['BS']),
 '유동부채':(['ifrs-full_CurrentLiabilities'],['유동부채'],['BS']),
 '투자현금흐름':(['ifrs-full_CashFlowsFromUsedInInvestingActivities'],['투자활동현금흐름','투자활동으로인한현금흐름'],['CF']),
 '재무현금흐름':(['ifrs-full_CashFlowsFromUsedInFinancingActivities'],['재무활동현금흐름','재무활동으로인한현금흐름'],['CF']),
 '유형자산취득':(['ifrs-full_PurchaseOfPropertyPlantAndEquipment'],['유형자산의취득'],['CF']),
})

def amount(raw):
    text=str(raw or '').replace(',','').strip()
    if text.startswith('(') and text.endswith(')'):text='-'+text[1:-1]
    try:
        value=float(text)
        return value if math.isfinite(value) else None
    except ValueError:return None

def extract_financials(rows):
    out={};missing=[]
    for label,(ids,names,sections) in ACCOUNTS.items():
        pool=[r for r in rows if r.get('sj_div') in sections and r.get('currency','KRW')=='KRW']
        matches=[r for r in pool if r.get('account_id') in ids]
        if not matches:matches=[r for r in pool if re.sub(r'\s+','',r.get('account_nm','')) in names]
        values={amount(r.get('thstrm_amount')) for r in matches};values.discard(None)
        out[label]=next(iter(values)) if len(values)==1 else None
        if out[label] is None:missing.append(label)
    out['누락·모호']=missing
    receipt=next((r.get('rcept_no') for r in rows if re.fullmatch(r'\d{14}',r.get('rcept_no',''))),None)
    out['접수번호']=receipt
    return out

def financial_ratios(current,previous=None):
    def ratio(a,b):
        av=current.get(a);bv=current.get(b)
        return av/bv*100 if av is not None and bv is not None and bv>0 else None
    result={'영업이익률':ratio('영업이익','매출액'),'순이익률':ratio('순이익','매출액'),'부채비율':ratio('부채','자본')}
    equity=current.get('자본');before=(previous or {}).get('자본');profit=current.get('순이익')
    result['ROE']=profit/((equity+before)/2)*100 if profit is not None and equity is not None and before is not None and equity>0 and before>0 else None
    revenue=current.get('매출액');old=(previous or {}).get('매출액')
    result['매출 증가율']=(revenue/old-1)*100 if revenue is not None and old is not None and old>0 else None
    return result
