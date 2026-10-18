"""공식 거시 데이터 수집. 캐시와 관측일·조회일을 별도로 보존합니다."""
import io
import json
import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import httpx
import pandas as pd

KST = ZoneInfo('Asia/Seoul')
CACHE = Path(__file__).resolve().parent / 'macro_cache'
COUNTRIES = {'USA':('미국','US'),'CHN':('중국','CN'),'EMU':('유로존','XM'),
 'JPN':('일본','JP'),'GBR':('영국','GB'),'DEU':('독일','DE'),'FRA':('프랑스','FR'),
 'ITA':('이탈리아','IT'),'ESP':('스페인','ES'),'CHE':('스위스','CH'),
 'KOR':('한국','KR'),'IND':('인도','IN'),'TWN':('대만','TW'),'IDN':('인도네시아','ID'),
 'AUS':('호주','AU'),'SGP':('싱가포르','SG'),'CAN':('캐나다','CA'),'MEX':('멕시코','MX'),
 'BRA':('브라질','BR'),'SAU':('사우디아라비아','SA'),'RUS':('러시아','RU'),
 'TUR':('튀르키예','TR'),'ZAF':('남아프리카공화국','ZA'),
 'NLD':('네덜란드','NL'),'POL':('폴란드','PL'),'SWE':('스웨덴','SE'),
 'NOR':('노르웨이','NO'),'ARE':('아랍에미리트','AE'),'THA':('태국','TH'),'VNM':('베트남','VN')}
# 이름, 단위, 세계은행 코드
INDICATORS = {
 'cpi':('CPI 상승률','% · 연평균 전년 대비','FP.CPI.TOTL.ZG'),
 'gdp':('실질 GDP 성장률','% · 연간','NY.GDP.MKTP.KD.ZG'),
 'unemployment':('실업률','% · 연간, ILO 추정','SL.UEM.TOTL.ZS'),
 'gdp_size':('명목 GDP','미 달러 · 연간','NY.GDP.MKTP.CD'),
 'exports':('수출 증가율','% · 상품·서비스 실질 연간','NE.EXP.GNFS.KD.ZG'),
 'imports':('수입 증가율','% · 상품·서비스 실질 연간','NE.IMP.GNFS.KD.ZG'),
 'current_account':('경상수지 / GDP','% · 연간','BN.CAB.XOKA.GD.ZS'),
 'consumption':('가계소비 증가율','% · 실질 연간','NE.CON.PRVT.KD.ZG'),
 'investment':('총자본형성 / GDP','% · 연간','NE.GDI.TOTL.ZS'),
 'money':('광의통화 증가율','% · 연간','FM.LBL.BMNY.ZG'),
 'fx':('공식 환율','현지통화 / USD · 연평균','PA.NUS.FCRF'),
 'debt':('중앙정부 부채 / GDP','% · 연간, 국가 간 범위 차이','GC.DOD.TOTL.GD.ZS')}
# 이름, 시리즈, 단위, 변환. 미국 PPI는 전체 상품 지수이며 최종수요 PPI와 다릅니다.
FRED = {
 '미국 CPI':('CPIAUCNS','% · 전년 동월 대비, 비계절조정','yoy'),
 '미국 근원 CPI':('CPILFESL','% · 전년 동월 대비, 계절조정','yoy'),
 '미국 PPI · 전체 상품':('PPIACO','% · 전년 동월 대비, 비계절조정','yoy'),
 '미국 PCE 물가':('PCEPI','% · 전년 동월 대비','yoy'),
 '미국 근원 PCE':('PCEPILFE','% · 전년 동월 대비','yoy'),
 '미국 실업률':('UNRATE','% · 월간','level'),
 '미국 비농업 고용 변화':('PAYEMS','천 명 · 전월 대비','diff'),
 '미국 산업생산':('INDPRO','% · 전년 동월 대비','yoy'),
 '미국 소매판매':('RSAFS','% · 명목 전년 동월 대비','yoy'),
 '미국 주택착공':('HOUST','천 호 · 연율 환산','level'),
 '미국 국채 2년':('DGS2','% · 일간','level'),
 '미국 국채 10년':('DGS10','% · 일간','level'),
 '미국 장단기 금리차 · 10년−2년':('T10Y2Y','%p · 일간','level'),
 '미국 광의 달러지수':('DTWEXBGS','지수 · DXY와 다름','level'),
 'WTI 유가':('DCOILWTICO','USD / 배럴','level'),
 'Brent 유가':('DCOILBRENTEU','USD / 배럴','level'),
 'VIX':('VIXCLS','지수','level'),
 '원/달러':('DEXKOUS','KRW / USD','level'),
 '위안/달러':('DEXCHUS','CNY / USD','level'),
 '한국 PPI · 제조업 내수':('KORPPDMMINMEI','% · 전년 동월 대비','yoy'),
 '일본 PPI · 제조업 내수':('JPNPPDMMINMEI','% · 전년 동월 대비','yoy'),
 '영국 PPI · 제조업 내수':('PIEAMP02GBM659N','% · 전년 동월 대비','level'),
 '중국 PPI · 산업 전체':('PIEATI01CNM659N','% · 전년 동월 대비','level')}


def now():
    return datetime.now(KST)


def fetch(url, ttl=3600, refresh=False):
    CACHE.mkdir(exist_ok=True)
    base = CACHE / hashlib.sha256(url.encode()).hexdigest()
    body, meta = base.with_suffix('.bin'), base.with_suffix('.json')
    old = None
    if body.exists() and meta.exists():
        try:
            old = json.loads(meta.read_text())
            age = (now() - datetime.fromisoformat(old['fetched_at'])).total_seconds()
            if age < ttl and not refresh:
                return body.read_bytes(), {**old, 'cached':True, 'stale':False}
        except (ValueError, OSError, KeyError):
            old = None
    try:
        response = httpx.get(url, timeout=35, follow_redirects=True,
                             headers={'User-Agent':'MacroAtlasResearch/1.0'})
        response.raise_for_status()
        data = response.content
        info = {'url':url, 'fetched_at':now().isoformat(), 'cached':False, 'stale':False}
        body.write_bytes(data)
        meta.write_text(json.dumps(info))
        return data, info
    except httpx.HTTPError:
        if old:
            return body.read_bytes(), {**old, 'cached':True, 'stale':True}
        raise ValueError('데이터 연결 실패. 잠시 후 새로고침해주세요.') from None


def world_bank(key, refresh=False):
    code = INDICATORS[key][2]
    countries = ';'.join(c for c in COUNTRIES if c != 'TWN')
    url = f'https://api.worldbank.org/v2/country/{countries}/indicator/{code}?format=json&per_page=20000&date=2000:{now().year}'
    raw, meta = fetch(url, 21600, refresh)
    payload = json.loads(raw)
    if not isinstance(payload, list) or len(payload)<2 or not isinstance(payload[1],list):
        raise ValueError('세계은행 응답에 관측값이 없습니다.')
    rows = [{'country':r['countryiso3code'], 'date':f"{r['date']}-01-01", 'value':r['value']}
            for r in payload[1] if r.get('value') is not None and r['countryiso3code'] in COUNTRIES]
    frame = pd.DataFrame(rows, columns=['country','date','value'])
    frame['date'] = pd.to_datetime(frame['date'])
    return frame.sort_values('date'), meta


def policy_rates(refresh=False):
    url = 'https://data.bis.org/static/bulk/WS_CBPOL_csv_col.zip'
    raw, meta = fetch(url, 21600, refresh)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        frame = pd.read_csv(archive.open(archive.namelist()[0]), low_memory=False)
    frame = frame[frame['FREQ']=='D']
    reverse = {v[1]:k for k,v in COUNTRIES.items()}
    from bis_frame import long_frame
    result=long_frame(frame,reverse,definitions=True)
    if result.empty:raise ValueError('BIS 정책금리 데이터 형식을 확인해주세요.')
    # 유로존 회원국은 ECB 공통 금리를 사용하되 출처가 유로존임을 표시합니다.
    euro=result[result.country=='EMU']
    for code in ('DEU','FRA','ITA','ESP','NLD'):
        copy=euro.copy();copy['country']=code
        result=pd.concat([result,copy],ignore_index=True)
    return result.sort_values('date'),meta


def fred(name, refresh=False):
    code,unit,transform=FRED[name]
    raw,meta=fetch(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}',3600,refresh)
    df=pd.read_csv(io.BytesIO(raw))
    if len(df.columns)!=2 or code not in df.columns:
        raise ValueError('시계열 응답을 확인하지 못했습니다.')
    df.columns=['date','value'];df['date']=pd.to_datetime(df.date)
    df['value']=pd.to_numeric(df.value,errors='coerce')
    df=df.sort_values('date').set_index('date')
    if transform in ('yoy','diff'):
        # 누락 월을 제거한 뒤 행 간격으로 계산하지 않습니다.
        df=df.resample('MS').last()
        df['value']=(df.value/df.value.shift(12)-1)*100 if transform=='yoy' else df.value.diff()
    return df.dropna().reset_index(),meta


FEEDS = {'BBC Business':'https://feeds.bbci.co.uk/news/business/rss.xml',
         'CNBC Economy':'https://www.cnbc.com/id/20910258/device/rss/rss.html',
         'Federal Reserve':'https://www.federalreserve.gov/feeds/press_all.xml',
         'ECB':'https://www.ecb.europa.eu/rss/press.html'}


def week_bounds(at=None):
    at=at or now();start=(at-timedelta(days=at.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
    return start,at


def news(refresh=False):
    start,end=week_bounds()
    def one(item):
        name,url=item
        try:
            raw,meta=fetch(url,1800,refresh)
            root=ET.fromstring(raw)
            items=[]
            for node in root.findall('.//item'):
                try:
                    dt=parsedate_to_datetime(node.findtext('pubDate')).astimezone(KST)
                except (TypeError,ValueError,AttributeError):
                    continue
                link=node.findtext('link','').strip()
                if start<=dt<=end and link.startswith('https://'):
                    from bs4 import BeautifulSoup
                    excerpt=BeautifulSoup(node.findtext('description',''),'html.parser').get_text(' ',strip=True)[:650]
                    items.append({'title':node.findtext('title',''),'excerpt':excerpt,'url':link,'published_at':dt.isoformat(),'source':name})
            return items, {'source':name,**meta}
        except Exception:
            return [],{'source':name,'error':'피드 조회 실패'}
    rows=[];statuses=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for items,status in pool.map(one,FEEDS.items()):
            rows.extend(items);statuses.append(status)
    unique={r['url']:r for r in rows}
    result=sorted(unique.values(),key=lambda r:r['published_at'],reverse=True)
    return result,statuses


def cpi_monthly(refresh=False):
    raw,meta=fetch('https://data.bis.org/static/bulk/WS_LONG_CPI_csv_col.zip',21600,refresh)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        f=pd.read_csv(archive.open(archive.namelist()[0]),low_memory=False)
    f=f[(f.FREQ=='M') & (f.UNIT_MEASURE.astype(str)=='771')]
    reverse={v[1]:k for k,v in COUNTRIES.items()}
    from bis_frame import long_frame
    result=long_frame(f,reverse,monthly=True)
    try:
        us,us_meta=fred('미국 CPI',refresh)
        if not us.empty:
            us=us.copy();us['country']='USA'
            result=pd.concat([result[result.country!='USA'],us[['country','date','value']]],ignore_index=True)
            meta={**meta,'us_source':us_meta,'us_definition':'BLS CPI-U, 비계절조정 전년동월비 (FRED)'}
    except (ValueError,KeyError):
        meta={**meta,'us_fallback':True}
    return result.sort_values('date'),meta


FRED['미국 신규 실업수당청구건수']=('ICSA','명 · 주간, 계절조정','level')
FEEDS.update({
 '연합뉴스 경제':'https://www.yna.co.kr/rss/economy.xml',
 '연합뉴스 산업':'https://www.yna.co.kr/rss/industry.xml',
 '연합뉴스 국제':'https://www.yna.co.kr/rss/international.xml',
 'CNBC Technology':'https://www.cnbc.com/id/19854910/device/rss/rss.html',
 'BBC Technology':'https://feeds.bbci.co.uk/news/technology/rss.xml'})


def japan_confidence(refresh=False):
    raw,meta=fetch('https://www.esri.cao.go.jp/en/stat/shouhi/shouhi2.xlsx',21600,refresh)
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        ss=[''.join(e.itertext()) for e in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        root=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    rows=[]
    for row in root.findall('.//s:row',ns):
        values={}
        for c in row.findall('s:c',ns):
            v=c.findtext('s:v',default='',namespaces=ns)
            values[re.sub(r'\d','',c.get('r',''))]=ss[int(v)] if c.get('t')=='s' and v else v
        token=values.get('A','')
        # 内閣府の年月キーは YYYY00MMMM。末尾2桁が月です。
        if re.fullmatch(r'\d{10}',token):
            year,month=int(token[:4]),int(token[-2:])
            val=pd.to_numeric(values.get('E'),errors='coerce')
            if 1<=month<=12 and pd.notna(val):rows.append({'date':f'{year}-{month:02}-01','value':float(val)})
    frame=pd.DataFrame(rows);frame['date']=pd.to_datetime(frame.date)
    return frame.sort_values('date'),meta


def euro_ppi(refresh=False):
    url='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inpp_m?lang=en&geo=EA20&unit=PCH_PRE&s_adj=NSA&nace_r2=B-D&sinceTimePeriod=2000-01'
    raw,meta=fetch(url,21600,refresh);d=json.loads(raw)
    if any(n!=1 for n in d['size'][:-1]):raise ValueError('Eurostat에 여러 계열이 반환되어 임의로 합치지 않았습니다.')
    times=d['dimension']['time']['category']['index']
    values=d.get('value',{});rows=[]
    for date,index in times.items():
        val=values.get(str(index)) if isinstance(values,dict) else values[index]
        if val is not None:rows.append({'date':date+'-01','value':val})
    frame=pd.DataFrame(rows,columns=['date','value']);frame['date']=pd.to_datetime(frame.date)
    if frame.empty:raise ValueError('유로존 PPI 관측값이 없습니다.')
    return frame.sort_values('date'),meta


def weekly_markets():
    import yfinance as yf
    tickers={'S&P 500':'^GSPC','FTSE 100':'^FTSE','CSI 300':'000300.SS','NIKKEI 225':'^N225',
             'KOSPI':'^KS11','Hang Seng':'^HSI','EURUSD':'EURUSD=X','USDCNY':'CNY=X',
             'USDJPY':'JPY=X','USDKRW':'KRW=X','BTCUSD':'BTC-USD','WTI 선물':'CL=F','금 선물':'GC=F'}
    start,end=week_bounds()
    def one(item):
        name,symbol=item
        try:
            h=yf.Ticker(symbol).history(period='1mo',auto_adjust=False)
            if h.empty:raise ValueError()
            dates=pd.to_datetime(h.index).tz_localize(None).normalize()
            h=h.copy();h['day']=dates
            before=h[h.day<pd.Timestamp(start.date())]
            current=h[(h.day>=pd.Timestamp(start.date()))&(h.day<=pd.Timestamp(end.date()))]
            if before.empty or current.empty:raise ValueError()
            base=float(before.Close.iloc[-1]);price=float(current.Close.iloc[-1])
            return {'지표':name,'값':price,'주간 변화 (%)':(price/base-1)*100,
                    '기준일':str(current.day.iloc[-1].date()),'비교일':str(before.day.iloc[-1].date()),
                    '출처':f'https://finance.yahoo.com/quote/{symbol}/','상태':'조회 성공 · 당일 봉은 장중일 수 있음'}
        except Exception:return {'지표':name,'상태':'조회 실패 · 값 미표시'}
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(one,tickers.items()))
    return rows


def korea_current_account(key, refresh=False):
    """ECOS 항목 목록에서 경상수지 항목을 찾고 통화 단위를 검증합니다."""
    CACHE.mkdir(exist_ok=True)
    path=CACHE/'korea_current_account.json'
    if path.exists() and not refresh:
        stored=json.loads(path.read_text())
        if (now()-datetime.fromisoformat(stored['fetched_at'])).total_seconds()<21600:
            frame=pd.DataFrame(stored['rows']);frame['date']=pd.to_datetime(frame.date)
            return frame,{'url':'https://ecos.bok.or.kr/','fetched_at':stored['fetched_at']}
    # 인증키가 포함된 요청 URL과 예외는 저장·출력하지 않습니다.
    def request(endpoint):
        try:
            r=httpx.get('https://ecos.bok.or.kr/api/'+endpoint,timeout=35,follow_redirects=False)
            r.raise_for_status();return r.json()
        except (httpx.HTTPError,ValueError):raise ValueError('ECOS 연결 실패. 인증키를 확인해주세요.') from None
    listing=request(f'StatisticItemList/{key}/json/kr/1/1000/301Y013')
    items=listing.get('StatisticItemList',{}).get('row',[])
    matches=[r for r in items if str(r.get('ITEM_NAME','')).strip()=='경상수지' and r.get('CYCLE')=='M']
    codes={r['ITEM_CODE'] for r in matches}
    if len(codes)!=1:raise ValueError('ECOS 경상수지 계정을 특정하지 못했습니다. 인증키·통계표를 확인해주세요.')
    code=next(iter(codes))
    end=now().strftime('%Y%m')
    result=request(f'StatisticSearch/{key}/json/kr/1/1000/301Y013/M/200001/{end}/{code}')
    rows=result.get('StatisticSearch',{}).get('row',[])
    clean=[]
    for r in rows:
        unit=r.get('UNIT_NAME','').replace(' ','')
        if '백만달러' in unit:scale=1000
        elif '십억달러' in unit:scale=1
        elif '억달러' in unit:scale=10
        else:raise ValueError('ECOS 통화 단위를 확인하지 못해 수치를 표시하지 않았습니다.')
        if re.fullmatch(r'\d{6}',r['TIME']):
            clean.append({'date':r['TIME'][:4]+'-'+r['TIME'][4:]+'-01','value':float(r['DATA_VALUE'])/scale})
    if not clean:raise ValueError('ECOS 경상수지 관측값을 가져오지 못했습니다.')
    stored={'rows':clean,'fetched_at':now().isoformat()};path.write_text(json.dumps(stored))
    frame=pd.DataFrame(clean);frame['date']=pd.to_datetime(frame.date)
    return frame.sort_values('date'),{'url':'https://ecos.bok.or.kr/','fetched_at':stored['fetched_at']}


def prioritize_news(articles):
    """로컬 생활기사보다 거시·주요 산업·국제시장 관련 뉴스를 우선합니다."""
    terms=['금리','물가','인플레이션','중앙은행','연준','한국은행','경상수지','국채','고용','실업',
           '수출','관세','무역','환율','코스피','나스닥','증시','유가','원유','opec','반도체','hbm',
           '엔비디아','ai','인공지능','부동산','중국 경제','gdp','소비','성장률','전쟁','중동',
           'inflation','interest rate','federal reserve','central bank','treasury','bond','tariff',
           'trade','oil','opec','semiconductor','chip','economy','economic','gdp','employment',
           'recession','stock','market','dollar','energy','china','euro','growth']
    def score(a):
        text=(a['title']+' '+a.get('excerpt','')).lower()
        value=sum(1 for term in terms if term in text)
        if a['source'] in ('Federal Reserve','ECB'):value+=5
        if any(t in text for t in ['[부산소식]','[영상]','프로야구','월드 챔피언십','고향사랑','가로수']):value-=5
        return value
    return sorted(articles,key=lambda a:(score(a),a['published_at']),reverse=True)
