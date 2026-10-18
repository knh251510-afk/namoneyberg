"""공식 발표 일정. 미국 동부시간을 DST를 반영해 한국시간으로 변환."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import macro_data as data

BEA='https://www.bea.gov/news/schedule/full'
BLS='https://www.bls.gov/schedule/2026/home.htm'
ET=ZoneInfo('America/New_York')
# 2026-10-16 공식 연간 일정 확인본. 자동 연결 차단 시에만 사용.
BLS_SNAPSHOT=[('2026-10-16','08:30','수출입물가'),('2026-10-30','08:30','고용비용지수'),
('2026-11-03','10:00','JOLTS 구인·이직'),('2026-11-05','08:30','생산성·비용'),
('2026-11-06','08:30','비농업 고용·실업률'),('2026-11-10','08:30','CPI 소비자물가'),
('2026-11-13','08:30','PPI 생산자물가'),('2026-11-17','08:30','수출입물가'),
('2026-12-01','10:00','JOLTS 구인·이직'),('2026-12-04','08:30','비농업 고용·실업률'),
('2026-12-08','08:30','생산성·비용'),('2026-12-10','08:30','CPI 소비자물가'),
('2026-12-15','08:30','PPI 생산자물가'),('2026-12-17','08:30','수출입물가')]

def event(day,time,title,source,url):
    dt=datetime.strptime(day+' '+time,'%Y-%m-%d %H:%M').replace(tzinfo=ET).astimezone(data.KST)
    return dict(when=dt,country='미국',title=title,source=source,url=url,time_known=True)

def parse_bea(raw):
    soup=BeautifulSoup(raw,'html.parser');events=[]
    for table in soup.select('table'):
        match=re.search(r'Year\s+(\d{4})',table.get_text(' ',strip=True))
        if not match:continue
        for row in table.select('tr'):
            date=row.select_one('.release-date');clock=row.select_one('.scheduled-date small');title=row.select_one('.release-title')
            if not all((date,clock,title)):continue
            try:
                dt=datetime.strptime(f'{date.get_text(strip=True)} {match[1]} {clock.get_text(strip=True)}','%B %d %Y %I:%M %p')
                text=title.get_text(' ',strip=True)
                if 'Gross Domestic Product' in text and 'by State' not in text and 'by County' not in text:text='GDP · '+text
                elif 'Personal Income and Outlays' in text:text='PCE·개인소득·소비 · '+text
                elif 'International Trade' in text:text='무역수지 · '+text
                else:continue
                events.append(event(dt.strftime('%Y-%m-%d'),dt.strftime('%H:%M'),text,'BEA',BEA))
            except ValueError:continue
    if not events:raise ValueError('BEA 일정 형식 변경')
    return events

def load():
    from calendar_global import events as global_events
    events=global_events()+[event(*e,'BLS',BLS) for e in BLS_SNAPSHOT];statuses=['한국·일본·유로존·영국 중앙은행과 한국 물가·고용·산업 일정: 공식 2026 계획 확인본 (2026-10-18). 시간 미정은 임의 추정하지 않습니다.']
    snapshot=Path(__file__).with_name('calendar_bls_history.json')
    if snapshot.exists():
        for item in json.loads(snapshot.read_text())['rows']:
            dt=datetime.strptime(item['day']+' '+item['time'],'%B %d, %Y %I:%M %p')
            events.append(event(dt.strftime('%Y-%m-%d'),dt.strftime('%H:%M'),item['title'],'BLS',f'https://www.bls.gov/schedule/{dt.year}/home.htm'))
    statuses.append('BLS: 2026-10-16 공식 일정 확인본 · 자동 접근 차단으로 저장된 일정 사용 · 변경 여부는 원문 확인')
    import quote_cache
    def bea():
        raw,meta=data.fetch(BEA,21600)
        return parse_bea(raw)
    more=quote_cache.request('calendar-bea',bea,lambda:[],ttl=21600)
    events+=more
    statuses.append('BEA: 공식 일정 연결' if more else 'BEA: 연결된 일정이 준비되면 추가합니다.')
    return pd.DataFrame(events).drop_duplicates(subset=['when','title']).sort_values('when'),statuses

@st.fragment(run_every=15)
def render():
    st.subheader('주요 경제지표 발표 일정')
    st.caption('한국 · 미국 · 일본 · 유로존 · 영국 | 한국시간')
    mode=st.segmented_control('표시 기간',['앞으로 30일','최근 1개월','최근 3개월','최근 1년','직접 선택'],default='앞으로 30일') or '앞으로 30일'
    with st.spinner('공식 발표 일정 조회 중…'):frame,status=load()
    countries=st.multiselect('경제권', ['한국','미국','일본','유로존','영국'],default=['한국','미국','일본','유로존','영국'])
    frame=frame[frame.country.isin(countries)]
    from calendar_explain import explain,importance
    levels=st.segmented_control('중요도',[1,2,3],format_func=lambda n:'★'*n,selection_mode='multi',default=[1,2,3])
    frame=frame[frame.title.map(lambda title:explain(title)[0] in (levels or []))]
    current=data.now();earliest=(pd.Timestamp(current.date())-pd.DateOffset(years=1)).date()
    if mode=='직접 선택':
        bounds=st.date_input('조회 기간',(earliest,current.date()),min_value=earliest,max_value=(current+timedelta(days=90)).date())
        if len(bounds)!=2:return
        lo,hi=bounds
    elif mode=='앞으로 30일':lo,hi=current.date(),(current+timedelta(days=30)).date()
    else:
        months={'최근 1개월':1,'최근 3개월':3,'최근 1년':12}[mode]
        lo=(pd.Timestamp(current.date())-pd.DateOffset(months=months)).date();hi=current.date()
    frame=frame[(frame.when.dt.date>=lo)&(frame.when.dt.date<=hi)]
    if mode!='앞으로 30일':frame=frame.sort_values('when',ascending=False)
    if frame.empty:st.info('이 기간에 확인된 발표 일정이 없습니다.')
    from html import escape
    import calendar_values
    import calendar_decisions
    import calendar_international_values
    import quote_cache,hashlib
    signature='|'.join(str(row['when'])+row['country']+row['title'] for _,row in frame.iterrows())
    lookup_key='calendar-values-v2-'+hashlib.sha256(signature.encode()).hexdigest()[:16]
    def fetch_values():
        return {'lookup':calendar_values.collect(frame[frame.country=='미국'],current),'international':calendar_international_values.collect(frame,current),'decisions':calendar_decisions.collect(frame,current)}
    payload=quote_cache.request(lookup_key,fetch_values,lambda:{'lookup':calendar_values.saved_lookup(),'international':None,'decisions':calendar_decisions.saved_results()},ttl=3600)
    lookup=payload['lookup'];international=payload['international']
    st.caption('중요도 ★★★ 높음 · ★★☆ 보통 · ★☆☆ 참고 | 지표 이름에 커서를 올리면 설명을 볼 수 있습니다.')
    for day,group in frame.groupby(frame.when.dt.strftime('%Y.%m.%d'),sort=False):
        weekday=group.iloc[0]['when'].weekday()
        st.markdown('<div class="calendar-day">'+day+' <span>'+['월','화','수','목','금','토','일'][weekday]+'요일</span></div>',unsafe_allow_html=True)
        numeric_rows=[];policy_rows=[]
        for _,row in group.iterrows():
            past=row['when']<current
            val=(calendar_values.values(row,lookup) if row['country']=='미국' else calendar_international_values.values(row,international)) if past else None
            name=row['title'].split(' · ')[0]
            if val:
                name=val['name'];period=val['period']
                actual=f'{val["value"]:,.2f} <small>{val["unit"]}</small>'
                previous='—' if val['previous'] is None or pd.isna(val['previous']) else f'{val["previous"]:,.2f}'
                delta=val['change']
                cls='rise' if delta is not None and delta>0 else ('fall' if delta is not None and delta<0 else 'flat')
                change='—' if delta is None else f'{delta:+,.2f} {val["delta_unit"]}'
                if val['mom'] is not None and pd.notna(val['mom']) and val['name'].startswith('CPI'):
                    change+=f'<small>물가지수 전월비 {val["mom"]:+.2f}% · 비계절조정</small>'
            else:
                period='';actual='—';previous='—';change='—';cls='flat'
            badge='지난 일정' if past else '발표 예정'
            clock=row['when'].strftime('%H:%M') if row.get('time_known',True) else '시간 미정'
            score,description=explain(row['title'])
            currency={'한국':'KRW','미국':'USD','일본':'JPY','유로존':'EUR','영국':'GBP'}.get(row['country'],'')
            tip='<span class="cal-event-name" tabindex="0">'+escape(name)+'<span class="cal-tooltip" role="tooltip">'+escape(description)+'</span></span>'
            if calendar_decisions.is_policy(row['title']):
                decision=calendar_decisions.result(row,payload.get('decisions',[])) if past else None
                if decision:
                    excerpt=decision['summary'] or decision['title']
                    cells='<td colspan="3" class="cal-decision"><strong>핵심 결정 · 안건</strong><p>'+escape(excerpt)+'</p><a href="'+escape(decision['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">공식 발표 ↗</a></td>'
                else:
                    text='공식 결과를 확인 중입니다.' if past else '회의 결과 발표 예정'
                    cells='<td colspan="3" class="cal-decision">'+text+'</td>'
            else:cells=f'<td class="cal-number">{actual}</td><td class="cal-number">{previous}</td><td class="cal-number {cls}">{change}</td>'
            target=policy_rows if calendar_decisions.is_policy(row['title']) else numeric_rows
            target.append(f'<tr><td class="cal-time">{clock}</td><td class="cal-country">{escape(row["country"])}<small>{currency}</small></td><td class="cal-impact" aria-label="중요도 {score}/3" title="사이트 편집 기준 중요도 {score}/3">{importance(score)}</td><td class="cal-title">{tip}<small>{escape(period)} · {badge} · <a href="{escape(row["url"],quote=True)}" target="_blank" rel="noopener noreferrer">출처 ↗</a></small></td>{cells}</tr>')
        for rows,heading in [(numeric_rows,'<th>실적</th><th>이전</th><th>증감</th>'),(policy_rows,'<th colspan="3">핵심 결정 · 안건</th>')]:
            if rows:st.markdown('<div class="calendar-table-wrap"><table class="calendar-table"><thead><tr><th>시간</th><th>경제권</th><th>중요도</th><th>경제지표</th>'+heading+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>',unsafe_allow_html=True)
    with st.expander('실적 출처 · 계산 기준',expanded=False):
        st.caption('한국 CPI는 BIS의 한국 월간 전년동월비를 발표 대상월과 일치할 때만 표시합니다. 한국 고용·산업활동의 실적은 아직 연결하지 않았습니다. 정책회의는 같은 발표일의 공식 보도자료를 연결합니다. 발표 일정은 실적 값이 없어도 표시합니다.')
        st.caption('현재 FRED 시계열을 발표 대상월과 연결합니다. 초도 발표 당시 수치와 다를 수 있습니다. GDP 추정차수·복수 대상월 등 일치 여부를 확인하지 못한 항목은 —로 표시합니다. 물가 상승률 간 차이는 %p, 고용 증감 간 차이는 천 명으로 계산합니다.')
        for code,result in lookup.items():
            if result and not code.startswith('_'):st.markdown(f'[{code}](https://fred.stlouisfed.org/series/{code})')
    with st.expander('일정 출처 · 연결 상태',expanded=False):
        for item in status:st.caption(item)
        st.markdown(f'[미국 BLS 공식 일정]({BLS}) · [미국 BEA 공식 일정]({BEA})')
        from calendar_global import SOURCES
        for label,url in SOURCES.items():st.markdown(f'[{label} 공식 일정]({url})')
