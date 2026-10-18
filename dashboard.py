"""GLOBAL MACRO ATLAS — 로컬 거시경제 대시보드."""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st
import api_settings as settings
import macro_data as data
import ui_theme
import comparison_ui
import portal_ui
import market_ui
import chart_ui
import admin_auth
import briefing_controls
import briefing_ui

st.set_page_config(page_title='NAMONEYBERG',page_icon='🌐',layout='wide')
ui_theme.apply()
with st.container(key='site_header'):
    logo_col,menu_col=st.columns([2,8],vertical_alignment='center')
    with logo_col:
        st.markdown('<div class="brand-head"><div class="brand-name"><b>NAMONEYBERG</b></div></div>',unsafe_allow_html=True)
    with menu_col:
        nav_slot=st.container(key='main_navigation')
st.markdown('<footer class="terminal-footer"><b>NAMONEYBERG</b><nav aria-label="관리 메뉴"><a href="/admin">관리자</a><a href="/sources">데이터 안내</a></nav></footer>',unsafe_allow_html=True)
market_ui.ticker()

@st.cache_data(ttl=1800,show_spinner=False)
def get_series(kind,key=''):
    if kind=='wb':return data.world_bank(key)
    if kind=='policy':return data.policy_rates()
    if kind=='fred':return data.fred(key)
    if kind=='cpi':return data.cpi_monthly()
    if kind=='euro_ppi':return data.euro_ppi()
    if kind=='jp_confidence':return data.japan_confidence()


if st.session_state.get('source_revision') != '20261016-cpi-v2':
    get_series.clear()
    st.session_state['source_revision']='20261016-cpi-v2'

def fetch_safe(kind,key=''):
    try:return (*get_series(kind,key),None)
    except Exception:return pd.DataFrame(),{},'조회 실패 또는 데이터 없음'


def label(code):return data.COUNTRIES[code][0]



def chart(frame,unit,year,group='country'):
    if frame.empty:
        st.info('선택한 조건에 관측 데이터가 없습니다.');return frame
    slot=st.container()
    import hashlib
    key='graph_'+hashlib.md5((unit+group+str(frame.get('series',pd.Series()).iloc[0] if 'series' in frame else '')).encode()).hexdigest()[:10]
    f=frame[frame.date.dt.year>=2000].copy()
    if group=='country':f=f[f.country.isin(selected)]
    with slot:
        if f.empty:st.info('선택한 조건에 관측 데이터가 없습니다.')
        else:
            f=f.copy();f['경제권']=f.country.map(label) if group=='country' else f[group]
            st.altair_chart(chart_ui.timeseries(f,'date','value',unit,group='경제권'),use_container_width=True,theme=None)
    return f


def source(meta,unit,frequency):
    if not meta:return
    st.caption(f"{frequency} · {unit} · 마지막 조회 {meta.get('fetched_at','미상')}")
    if meta.get('us_fallback'):st.warning('미국 최신 CPI 연결에 실패해 BIS 자료를 표시합니다. 관측월을 확인해주세요.')
    if meta.get('stale'):st.warning('연결 실패로 이전 저장 자료를 표시합니다. 최신 발표가 반영되지 않았을 수 있습니다.')
    with st.expander('출처 · 조회 정보',expanded=False):
        if meta.get('us_source'):
            st.caption(f"[미국 CPI: BLS / FRED]({meta['us_source']['url']}) · 비계절조정 전년동월비 · 조회 {meta['us_source']['fetched_at']}")
        st.caption(f"[데이터 원본]({meta['url']})")


def latest(frame):
    if frame.empty:return pd.DataFrame()
    ordered=frame.dropna(subset=['value']).sort_values('date').copy()
    ordered['previous']=ordered.groupby('country')['value'].shift()
    ordered['previous_date']=ordered.groupby('country')['date'].shift()
    ordered['change']=ordered['value']-ordered['previous']
    out=ordered.groupby('country').tail(1).copy()
    out['경제권']=out.country.map(label)
    return out

selected=['USA','CHN','EMU','JPN','KOR']
start_year=2000

@st.fragment(run_every=1800)
def auto_update():
    last=st.session_state.setdefault('last_refresh_clock',data.now().isoformat())
    if (data.now()-datetime.fromisoformat(last)).total_seconds()>=1800:
        st.session_state['last_refresh_clock']=data.now().isoformat()
        st.rerun()
auto_update()



def render_page(page,embedded=False):
    if not embedded and page not in ('세계 요약','API 설정','데이터 안내'):
        from html import escape
        st.markdown('<div class="page-heading"><div class="breadcrumb">홈 &nbsp; / &nbsp; '+escape(page)+'</div><h1>'+escape(page)+'</h1></div>',unsafe_allow_html=True)

    if page=='데이터 비교':
        import data_compare_ui
        data_compare_ui.render(fetch_safe)
        return

    if page=='경제지표':
        import indicators_ui
        indicators_ui.render(fetch_safe)
        return

    if page=='세계 요약':
        st.markdown(f'<div class="edition-line"><span>주요국 정책금리</span><span>{data.now():%Y.%m.%d} 기준</span></div>',unsafe_allow_html=True)
        with st.spinner('공식 통계와 금리를 불러오고 있습니다…'):
            jobs=[('cpi',''),('wb','gdp'),('wb','unemployment'),('policy','')]
            with ThreadPoolExecutor(max_workers=4) as pool:
                results=list(pool.map(lambda job:fetch_safe(*job),jobs))
        table=pd.DataFrame({'country':list(data.COUNTRIES)})
        titles=['CPI · 전년동월 %','GDP 성장 · 연간 %','실업률 · 연간 %','정책금리 · %']
        for title,(frame,meta,error) in zip(titles,results):
            if error:st.warning(f'{title}: {error}')
            l=latest(frame)
            if not l.empty:
                l=l[['country','value','date','previous','change','previous_date']].rename(columns={'value':title,'date':title+' 관측','previous':title+' 이전','change':title+' 증감','previous_date':title+' 이전 관측'})
                l[title+' 관측']=l[title+' 관측'].dt.strftime('%Y-%m-%d')
                table=table.merge(l,on='country',how='left')
        table['경제권']=table.country.map(label)
        st.session_state['annual_snapshot']=table.to_json(orient='records',force_ascii=False)
        visible=table[table.country.isin(selected)] if selected else table
        policy_frame=results[3][0]
        changes=portal_ui.policy_changes(policy_frame)
        portal_ui.strip(visible,changes)
        render_page('이번 주 마켓 오버뷰',embedded=True)
    elif page=='물가 · 정책금리':
        indicator=st.segmented_control('지표',['CPI · 월간 전년동월비','정책금리','CPI · 연평균 상승률','PPI · 국가별 상세'],default='CPI · 월간 전년동월비') or 'CPI · 월간 전년동월비'
        if indicator=='PPI · 국가별 상세':
            options=[k for k in data.FRED if 'PPI' in k]
            choice=st.selectbox('계열 선택',options)
            frame,meta,error=fetch_safe('fred',choice)
            if error:st.warning(error)
            else:
                frame['series']=choice;chart(frame,data.FRED[choice][1],start_year,'series')
                source(meta,data.FRED[choice][1],'월간')
                st.warning('PPI는 국가별 산업 범위가 다릅니다. 여기서는 5개 경제권의 계열만 연결했으며 다른 국가를 임의 추정하지 않습니다.')
        else:
            kind,key=('cpi','') if indicator.startswith('CPI · 월간') else (('policy','') if indicator=='정책금리' else ('wb','cpi'))
            with st.spinner('시계열 조회 중…'):frame,meta,error=fetch_safe(kind,key)
            if error:st.warning(error)
            else:
                subset=chart(frame,'%',start_year)
                l=latest(subset)
                if not l.empty:comparison_ui.render(l,[('최신 관측','value','date','%',True)])
                source(meta,'%', '일간' if kind=='policy' else ('월간' if kind=='cpi' else '연간'))
                if kind=='policy':
                    st.caption('미국은 목표범위 중간값 등 BIS 국가별 정의를 사용합니다. ECB 계열은 역사적으로 정책수단이 변경됩니다.')
                    with st.expander('국가별 금리 정의'):
                        st.dataframe(subset[['country','definition']].drop_duplicates().assign(country=lambda f:f.country.map(label)),use_container_width=True)

    elif page=='경기 · 무역 비교':
        key=st.segmented_control('지표',list(data.INDICATORS),default='gdp',format_func=lambda k:data.INDICATORS[k][0]) or 'gdp'
        name,unit,code=data.INDICATORS[key]
        st.subheader(name)
        with st.spinner('세계은행 통계를 불러오고 있습니다…'):frame,meta,error=fetch_safe('wb',key)
        if error:st.warning(error)
        else:
            bar_slot=st.container()
            f=frame[frame.country.isin(selected)]
            same_year=False
            if same_year and not f.empty:
                year=st.selectbox('비교 연도',sorted(f.date.dt.year.unique(),reverse=True))
                l=f[f.date.dt.year==year].copy();l['경제권']=l.country.map(label)
            else:l=latest(f)
            if not l.empty:
                bar_slot.altair_chart(alt.Chart(l).mark_bar(color='#527fb2').encode(
                    x=alt.X('경제권:N',sort='-y',axis=alt.Axis(labelAngle=0,title=None)),y=alt.Y('value:Q',title=unit),
                    tooltip=['경제권',alt.Tooltip('date:T',format='%Y'),alt.Tooltip('value:Q',format=',.2f')]
                ).properties(height=280),use_container_width=True)
            chart(frame,unit,start_year);source(meta,unit,'연간')
            if not l.empty:comparison_ui.render(l,[(name,'value','date',unit,False)])
            missing=[label(c) for c in selected if c not in set(f.country)]
            if missing:st.info('자료 미제공: '+', '.join(missing))

    elif page=='시장 · 고빈도 지표':
        choice=st.selectbox('시계열',list(data.FRED))
        with st.spinner('FRED 데이터를 불러오고 있습니다…'):frame,meta,error=fetch_safe('fred',choice)
        if error:st.warning(error)
        elif not frame.empty:
            last=frame.iloc[-1];prev=frame.iloc[-2] if len(frame)>1 else None
            st.metric(choice,f"{last.value:,.2f}",None if prev is None else f"{last.value-prev.value:+.2f} · 직전 관측 대비")
            st.caption(f'마지막 관측: {last.date:%Y-%m-%d}')
            frame['series']=choice;chart(frame,data.FRED[choice][1],start_year,'series')
            source(meta,data.FRED[choice][1],'계열별 일간·월간')
            age=(pd.Timestamp(data.now().date())-last.date).days
            if age>100:st.warning(f'마지막 관측이 {age}일 전입니다. 중단·지연 계열일 수 있으므로 최신 지표로 사용하지 마세요.')
            with st.expander('지표 정의 · 발표 주기',expanded=False):
                st.caption(f"[FRED 계열 안내](https://fred.stlouisfed.org/series/{data.FRED[choice][0]})")

    elif page=='경제 용어':
        import glossary_ui
        glossary_ui.render()

    elif page=='시장 시세':
        market_ui.render()

    elif page=='경제지표 일정':
        import economic_calendar
        economic_calendar.render()

    elif page in ('이번 주 마켓 오버뷰','LOE 위클리'):
        start,end=data.week_bounds()
        st.markdown('<div id="weekly-review" class="section-heading"><div><h2>이번 주 마켓 오버뷰</h2></div></div>',unsafe_allow_html=True)
        st.caption(f'{start:%Y-%m-%d %H:%M} ~ {end:%Y-%m-%d %H:%M} · 한국시간 · 월요일 시작')
        refresh=False
        articles=[];statuses=[]
        if admin_auth.is_admin():
            with st.spinner('브리핑 자료 준비 중…'):
                articles,statuses=data.news(False)
                articles=data.prioritize_news(articles)
        if page=='LOE 위클리':
            st.markdown('### 거시지표 업데이트')
            watch=[('유로존 PPI 전월비','euro_ppi','', '%'),('미국 신규 실업수당청구건수','fred','미국 신규 실업수당청구건수','천 명'),('일본 소비자신뢰지수','jp_confidence','','지수')]
            rows=[]
            with ThreadPoolExecutor(max_workers=3) as pool:
                outputs=list(pool.map(lambda w:fetch_safe(w[1],w[2]),watch))
            for w,(f,meta,error) in zip(watch,outputs):
                row={'지표':w[0],'단위':w[3],'예상':None,'상태':error or '자동 조회'}
                if not f.empty:
                    factor=1000 if w[1]=='fred' else 1
                    row.update({'발표값':float(f.value.iloc[-1])/factor,'이전':float(f.value.iloc[-2])/factor if len(f)>1 else None,'관측기간':f.date.iloc[-1].strftime('%Y-%m-%d'),'출처':meta['url']})
                    if (pd.Timestamp(data.now().date())-f.date.iloc[-1]).days>100:row['상태']='관측 지연 · 날짜 확인'
                rows.append(row)
            ca=None
            ecos_key=settings.read_key('ECOS')
            if ecos_key:
                try:
                    ca=data.korea_current_account(ecos_key)
                except ValueError as error:
                    st.warning(str(error)+' API 설정 탭에서 키를 확인해주세요.')
            else:
                st.caption('한국 경상수지: API 설정 탭에서 ECOS 키를 한 번 저장하면 자동 갱신됩니다.')
            if not ca:
                try:
                    cached_ca=data.CACHE/'korea_current_account.json'
                    if cached_ca.exists():
                        stored=json.loads(cached_ca.read_text());f=pd.DataFrame(stored['rows']);f['date']=pd.to_datetime(f.date)
                        ca=(f,{'url':'https://ecos.bok.or.kr/','fetched_at':stored['fetched_at']})
                except Exception:pass
            if ca:
                cf,cm=ca
                rows.append({'지표':'한국 경상수지','단위':'십억 USD · 월간','발표값':float(cf.value.iloc[-1]),'이전':float(cf.value.iloc[-2]) if len(cf)>1 else None,'예상':None,'관측기간':cf.date.iloc[-1].strftime('%Y-%m'),'상태':'ECOS 저장 자료 · 조회 '+cm['fetched_at'],'출처':cm['url']})
            else:rows.append({'지표':'한국 경상수지','단위':'십억 USD · 월간','발표값':None,'이전':None,'예상':None,'상태':'한국은행 ECOS 인증키 연결 필요','출처':'https://ecos.bok.or.kr/'})
            st.session_state['release_snapshot']=rows
            comparison_ui.compact(pd.DataFrame(rows),[('지표','지표',None),('발표값','발표값',2),('이전','이전',2),('예상','예상',2),('단위','단위',None),('관측기간','관측기간',None)],'지표')
            with st.expander('지표별 출처',expanded=False):
                for row in rows:
                    if row.get('출처'):st.caption(f"[{row['지표']}]({row['출처']})")
            st.caption('예상치는 컨센서스 공급원이 연결되지 않아 비워둡니다. 이전값은 현재 데이터베이스의 수정값이며 발표 당시 수치와 다를 수 있습니다.')
            detail=st.selectbox('LOE 추적 지표 그래프',[w[0] for w in watch])
            i=[w[0] for w in watch].index(detail);f,meta,error=outputs[i]
            if not f.empty:
                f=f.copy();f['series']=detail
                if watch[i][1]=='fred':f['value']=f.value/1000
                chart(f,watch[i][3],start_year,'series')
            st.markdown('### 시장지표 · 주간 변화')
            if st.button('시장지표 불러오기 · 갱신'):
                with st.spinner('주요 지수·환율·원자재의 주간 변화를 계산하고 있습니다…'):
                    st.session_state['weekly_markets']=data.weekly_markets()
            markets=st.session_state.get('weekly_markets',[])
            if markets:
                mf=pd.DataFrame(markets)
                comparison_ui.compact(mf,[('시장','지표',None),('가격','값',2),('주간 변화 %','주간 변화 (%)',2),('기준일','기준일',None)],'지표')
                with st.expander('시장지표 출처',expanded=False):
                    for row in markets:
                        if row.get('출처'):st.caption(f"[{row['지표']}]({row['출처']})")
                good=mf.dropna(subset=['주간 변화 (%)']) if '주간 변화 (%)' in mf else pd.DataFrame()
                if not good.empty:
                    st.altair_chart(alt.Chart(good).mark_bar().encode(x='주간 변화 (%):Q',y=alt.Y('지표:N',sort='-x'),color=alt.condition(alt.datum['주간 변화 (%)']>=0,alt.value('#839581'),alt.value('#b29c8c')),tooltip=['지표','값','주간 변화 (%)','기준일','비교일']).properties(height=330),use_container_width=True)
            st.caption('주간 변화는 이전 주 마지막 관측과 이번 주 최신 관측을 비교합니다. 원유·금은 선물이며 가격과 휴장일은 시장마다 다릅니다.')
        for status in statuses:
            if status.get('error') or status.get('stale'):st.warning(status['source']+' 연결 실패 또는 이전 저장 자료 사용')
        if briefing_controls.request_generation(bool(articles)):
            if not admin_auth.is_admin():st.stop()
            try:
                key=settings.read_key('OpenAI')
                model=settings.model_name()
                if not key:st.warning('API 설정 탭에서 OpenAI 키를 한 번 저장해주세요.')
                else:
                    with st.spinner('뉴스 근거를 종합하고 해석을 작성하고 있습니다…'):
                        from macro_ai import overview
                        context={'markets':st.session_state.get('weekly_markets',[]),'releases':st.session_state.get('release_snapshot',[]),'annual_data':st.session_state.get('annual_snapshot','未取得')}
                        report=overview(key,model,articles,context)
                        report['data_snapshot']=context
                        report['generated_at']=data.now().isoformat()
                        st.session_state['weekly_report']=report
                        folder=Path(__file__).resolve().parent/'macro_reports';folder.mkdir(exist_ok=True)
                        (folder/f'overview_{data.now():%Y%m%d_%H%M%S}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
            except Exception as error:
                from openai import APIStatusError
                if isinstance(error,APIStatusError):st.error(f'OpenAI 오류: HTTP {error.status_code} / {error.code or "미상"}')
                elif isinstance(error,ValueError):st.error(str(error))
                else:st.error('AI 요약 연결에 실패했습니다. 키·모델 접근 권한·네트워크를 확인해주세요.')
        saved=st.session_state.get('weekly_report')
        if not saved:
            folder=Path(__file__).resolve().parent/'macro_reports'
            for path in sorted(folder.glob('overview_*.json'),reverse=True):
                try:
                    candidate=json.loads(path.read_text())
                    if candidate['period']['start']==start.isoformat():
                        saved=candidate;st.session_state['weekly_report']=saved;break
                except (ValueError,KeyError,OSError):continue
        briefing_ui.metadata(briefing_controls.updated_label(saved))
        if saved and saved['period']['start']==start.isoformat():
            briefing_ui.metadata('브리핑 기준 '+saved['period']['start'][:10]+' ~ '+saved['period'].get('end','')[:10])
            r=saved['report']
            from html import escape
            st.markdown('<div class="brief-lead"><h3>'+escape(r['headline'])+'</h3><p>'+escape(r['summary'])+'</p></div>',unsafe_allow_html=True)
            category=briefing_ui.category_picker()
            themes=[t for t in r['themes'] if t.get('category')==category]
            if not themes:st.info('이 범주의 근거가 충분한 뉴스가 없습니다.')
            asset={'매크로':'macro','글로벌':'global','산업':'industry'}[category]
            blocks=[]
            for theme in themes:
                 sources=''.join('<a href="'+escape(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(item['source']+' · '+item['title'])+' ↗</a>' for item in theme['sources'])
                 blocks.append('<article class="brief-topic"><h4>'+escape(theme['title'])+'</h4><dl><dt>종합 흐름</dt><dd>'+escape(theme['facts'])+'</dd><dt>시장 의미</dt><dd>'+escape(theme['interpretation'])+'</dd><dt>확인할 변수</dt><dd>'+escape(theme['watch'])+'</dd></dl><details class="brief-sources"><summary>출처 '+str(len(theme['sources']))+'건</summary>'+sources+'</details></article>')
            st.markdown('<div class="brief-topics">'+''.join(blocks)+'</div>',unsafe_allow_html=True)
            briefing_ui.downloads(saved,start)
    elif page=='뉴스':
        from html import escape
        st.subheader('뉴스')
        if st.button('뉴스 새로고침'):
            st.session_state.pop('news_cache',None)
        with st.spinner('이번 주 뉴스 수집 중…'):
            articles,status=data.news()
        left,right=st.columns([3,2])
        query=left.text_input('기사 검색',placeholder='제목·언론사 검색')
        publisher=right.selectbox('언론사',['전체']+sorted({a['source'] for a in articles}))
        filtered=[a for a in articles if (publisher=='전체' or a['source']==publisher) and query.casefold() in (a['title']+' '+a['source']).casefold()]
        st.caption(f'{len(filtered)}건 · 이번 주')
        pages_count=max(1,(len(filtered)+39)//40)
        page_number=st.number_input('페이지',min_value=1,max_value=pages_count,value=1,step=1)
        for item in filtered[(page_number-1)*40:page_number*40]:
            stamp=datetime.fromisoformat(item['published_at']).strftime('%m/%d %H:%M')
            st.markdown('<div class="news-list-item">'+portal_ui.article_link(item)+'<small>'+escape(item['source'])+' · '+stamp+' KST</small></div>',unsafe_allow_html=True)
        if not filtered:st.info('조건에 맞는 기사가 없습니다.')

    elif page=='관리자':
        if not admin_auth.require_admin():return
        st.success('관리자로 로그인했습니다.')
        st.markdown('[브리핑 관리](/) · [API 설정](/settings)')
        if st.button('로그아웃'):admin_auth.logout()

    elif page=='API 설정':
        if not admin_auth.require_admin():return
        st.subheader('API 설정')
        st.write('여기서 한 번 저장하면 앱을 다시 열어도 자동으로 불러옵니다. 변경할 키만 입력하세요.')
        cols=st.columns(3)
        for col,name in zip(cols,settings.SERVICES):
            col.metric(name,'저장됨' if settings.read_key(name) else '미등록')
        st.caption('저장 상태는 인증 성공 여부를 의미하지 않습니다. 실제 기능 실행 시 유효성을 확인합니다.')
        with st.form('api_settings_form',clear_on_submit=True):
            openai_value=st.text_input('OpenAI API 키',type='password',help='주간 뉴스 요약에 사용합니다.')
            ecos_value=st.text_input('한국은행 ECOS API 키',type='password',help='한국 월간 경상수지에 사용합니다. DART 키와 별도입니다.')
            dart_value=st.text_input('DART API 키',type='password',help='기존 기업 분석 실습용입니다. 거시 대시보드에는 필요하지 않습니다.')
            chosen_model=st.text_input('OpenAI 모델',value=settings.model_name())
            submitted=st.form_submit_button('설정 저장',type='primary')
        if submitted:
            failures=[]
            for name,value in [('OpenAI',openai_value),('ECOS',ecos_value),('DART',dart_value)]:
                if value.strip():
                    try:settings.save_key(name,value)
                    except Exception:failures.append(name)
            settings.save_model(chosen_model)
            if failures:st.error('키체인 저장 실패: '+', '.join(failures)+'. Mac 키체인 접근을 허용했는지 확인해주세요.')
            else:
                st.success('설정을 저장했습니다. 분석 화면에서 자동으로 사용합니다.')
                st.rerun()
        st.info('키는 이 Mac의 키체인에 저장됩니다. 화면에 기존 키를 다시 노출하거나 결과 파일에 저장하지 않습니다. 키를 폐기·교체하면 여기서 새 키를 저장하세요.')
        st.markdown('[OpenAI 키 관리](https://platform.openai.com/api-keys) · [ECOS 키 발급](https://ecos.bok.or.kr/api/) · [DART 키 관리](https://opendart.fss.or.kr/)')

    else:
        st.subheader('출처와 해석 기준')
        st.markdown('''
    - **세계은행 WDI:** 12종의 연간 거시지표. 최신 월간 상황을 대신하지 않습니다. 대만은 이 API에서 제공하지 않습니다.
    - **BIS:** 중앙은행 정책금리와 소비자물가. 정책수단과 통계 정의는 국가별로 다릅니다.
    - **FRED:** 미국 물가·고용·경기, 채권·환율·유가·변동성, 일부 국가 PPI. 관측이 중단된 계열은 마지막 관측일로 판단해야 합니다.
    - **뉴스:** 한국시간 이번 주 RSS 발행분. 발행일은 사건 발생일과 다를 수 있습니다.
    - **AI 해설:** 수집한 뉴스 제목·RSS 제공 요약을 바탕으로 한 해석입니다. 원문 전체 분석이나 모든 사건의 검증을 의미하지 않습니다.

    자료를 누락값으로 표시하며 0으로 채우지 않습니다. 그래프는 관측 시점과 단위를 유지합니다.
    웹이 열려 있으면 30분마다 화면을 갱신하고 만료된 캐시를 재조회합니다. AI 요약은 버튼으로 별도 생성합니다. 컴퓨터가 꺼져 있거나 앱이 닫혀 있으면 자동 수집하지 않습니다.
    ''')
        st.dataframe(pd.DataFrame([{'지표':v[0],'단위':v[1],'코드':v[2],'주기':'연간'} for v in data.INDICATORS.values()]),use_container_width=True)
        st.caption('PMI, 각국 월간 소매판매·주택·신용 등은 아직 전체 국가에 연결되지 않았습니다. 데이터 공급원 확장 시 추가할 수 있습니다.')


PAGE_SPECS=[('세계 요약','마켓 오버뷰','overview'),('경제지표','경제지표','indicators'),('물가 · 정책금리','물가·금리','prices'),
            ('경기 · 무역 비교','경기·무역','economy'),('시장 · 고빈도 지표','시장지표','markets'),
            ('이번 주 마켓 오버뷰','마켓 오버뷰','weekly'),('뉴스','뉴스','news'),('경제지표 일정','경제지표 일정','calendar'),
            ('시장 시세','시장 시세','quotes'),('데이터 비교','데이터 비교','compare'),('경제 용어','경제 용어','glossary'),('관리자','관리자','admin'),('API 설정','API 설정','settings'),('데이터 안내','데이터 안내','sources')]
pages=[]
for original,title,slug in PAGE_SPECS:
    def make_page(name):
        def view():
            if name in ('물가 · 정책금리','경기 · 무역 비교','시장 · 고빈도 지표'):
                st.session_state['indicator_category']={'물가 · 정책금리':'물가·금리','경기 · 무역 비교':'경기·무역','시장 · 고빈도 지표':'시장지표'}[name]
                st.switch_page(next(p for p in pages if p.url_path=='indicators'))
            elif name=='이번 주 마켓 오버뷰':st.switch_page(pages[0])
            else:render_page(name)
        return view
    pages.append(st.Page(make_page(original),title=title,url_path=slug,default=slug=='overview'))
active=st.navigation(pages,position='hidden')
active_index=next((i for i,p in enumerate(pages) if p.url_path==active.url_path),0)
public_specs=[spec for spec in PAGE_SPECS if spec[2] not in ('settings','sources','weekly','admin','prices','economy','markets')]
active_spec=PAGE_SPECS[active_index]
if active_spec in public_specs:
    menu_index=public_specs.index(active_spec)+1
    st.markdown(f'<style>.st-key-main_navigation [data-testid="stElementContainer"]:nth-child({menu_index}) a{{background:var(--seed-color-bg-brand-weak)!important;color:var(--nb-accent)!important;border-bottom:0!important}}.st-key-main_navigation [data-testid="stElementContainer"]:nth-child({menu_index}) a p{{color:var(--nb-accent)!important;font-weight:600!important}}</style>',unsafe_allow_html=True)

with nav_slot:
    for spec,nav_page in zip(PAGE_SPECS,pages):
        if spec[2] not in ('settings','sources','weekly','admin','prices','economy','markets'):
            st.page_link(nav_page,label=spec[1])
if st.query_params.get('page')=='settings':
    del st.query_params['page']
    st.switch_page(next(p for p,spec in zip(pages,PAGE_SPECS) if spec[2]=='settings'))
with st.container(key="page_body"):
    active.run()
if st.session_state.pop('open_comparison',False):
    st.switch_page(next(p for p in pages if p.url_path=='compare'))
