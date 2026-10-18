"""DART annual financial analysis and disclosures, without LLM-generated figures."""
from datetime import date,timedelta
from html import escape
import pandas as pd
import streamlit as st
import api_settings
import analysis_sources as src
import chart_ui
import financial_model as model
from theme_tokens import colors
from ui_theme import mode

def render():
    palette=colors(mode())
    st.caption('공시 기반 재무제표 · 모델링 기초 데이터')
    key=api_settings.read_key('DART')
    if not key:
        st.info('기업 재무분석을 현재 이용할 수 없습니다. 데이터 연결을 준비 중입니다.')
        return
    try:
        companies=src.listed_companies()
        selected=st.selectbox('기업명 또는 종목코드',companies,index=None,
            format_func=lambda c:c['name']+' · '+c['stock_code'],
            placeholder='기업명 일부로 검색 · 예: 삼, 삼성, 005930')
        if selected is None:return
        company=selected
        a,b,c=st.columns(3)
        year=a.selectbox('사업연도',list(range(date.today().year-1,2014,-1)))
        basis=b.selectbox('재무제표',['CFS','OFS'],format_func=lambda x:'연결' if x=='CFS' else '별도')
        span=c.selectbox('비교 연수',[3,5],index=0)
        if st.button('재무분석 조회',type='primary'):
            frames=[];warnings=[];raw={};origins={}
            with st.spinner('DART 재무제표와 공시 조회 중…'):
                progress=st.empty()
                progress.caption('기업 고유번호 확인 중…')
                company=src.resolve_dart_company(company['stock_code'],key)
                from concurrent.futures import ThreadPoolExecutor, as_completed
                years_to_fetch=list(range(max(2015,year-span),year+1))
                def fetch_year(y):
                    try:
                        rows,origin=src.dart_statement_with_meta(company['corp_code'],int(y),basis,key)
                        return y,rows,None,origin
                    except src.SourceError as exc:return y,[],str(exc),{}
                fetched=[]
                with ThreadPoolExecutor(max_workers=4) as pool:
                    pending=[pool.submit(fetch_year,y) for y in years_to_fetch]
                    for future in as_completed(pending):
                        fetched.append(future.result())
                        progress.caption(f'연간 재무제표 {len(fetched)}/{len(years_to_fetch)}개 확인')
                progress.empty()
                for y,rows,error,origin in fetched:
                    origins[y]=origin
                    raw[y]=rows
                    if error:warnings.append(str(y)+'년: '+error);continue
                    if not rows:warnings.append(str(y)+'년 자료 없음');continue
                    values=src.extract_financials(rows);frames.append({'연도':y,**values})
                    if values['누락·모호']:warnings.append(str(y)+'년 확인 필요: '+', '.join(values['누락·모호']))
                notices=[]
            st.session_state['corporate_result']={'identity':(company['stock_code'],int(year),basis,span),'company':company,'rows':frames,'raw':raw,'notices':notices,'warnings':warnings,'origins':origins}
        saved=st.session_state.get('corporate_result')
        if not saved:return
        if saved['identity']!=(company['stock_code'],int(year),basis,span):
            st.info('조회 조건이 바뀌었습니다. 재무분석 조회를 눌러 새 조건으로 확인해주세요.')
            return
        financials=pd.DataFrame(saved['rows'])
        if financials.empty:
            st.info('선택한 기준의 연간 재무제표를 가져오지 못했습니다.')
            for note in saved['warnings']:st.caption(note)
            if st.button('DART 연결 상태 확인',key='dart_connection_check'):
                from dart_connection import diagnostics
                with st.spinner('기본 연결과 IPv4 직접 연결을 확인합니다…'):
                    st.session_state['dart_connection_diagnostics']=diagnostics(key)
                    from dart_network import diagnostics as network_diagnostics
                    st.session_state['dart_network_diagnostics']=network_diagnostics()
            diagnostic=st.session_state.get('dart_connection_diagnostics')
            if diagnostic:
                st.dataframe(pd.DataFrame(diagnostic),hide_index=True,width='stretch')
                st.caption('인증키와 요청 주소는 진단 결과에 포함하지 않습니다.')
                if st.session_state.get('dart_network_diagnostics'):
                    with st.expander('DNS · TCP · TLS 상세 진단'):
                        st.json(st.session_state['dart_network_diagnostics'])
            return
        financials=financials.sort_values('연도');latest=financials[financials.연도==year]
        if latest.empty:st.warning('선택 연도 자료가 없습니다. 과거 자료만 표시합니다.')
        st.caption(company['name']+' · '+('연결' if basis=='CFS' else '별도')+' · 연간 사업보고서 · 금액 KRW, 표시 단위 억 원')
        saved_origins={y:origin for y,origin in saved.get('origins',{}).items() if origin.get('saved')}
        if saved_origins:
            dates=[origin['retrieved_at'] for origin in saved_origins.values()]
            st.info('DART 저장 자료를 표시합니다. 마지막 수집: '+pd.Timestamp(max(dates)).tz_convert('Asia/Seoul').strftime('%Y.%m.%d %H:%M KST')+' · 미수집 연도는 —로 표시합니다.')
        years=list(range(int(year)-span+1,int(year)+1))
        st.download_button('엑셀 다운로드',model.export_xlsx(saved,years,basis),
                           file_name=company['stock_code']+'_fundamentals_'+basis+'.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.caption('열: 사업연도 · 행: 재무 계정 · 미제공·모호한 값은 — · 예측 전 단계의 과거 실적')
        for section,labels in model.SECTIONS.items():
            st.markdown('#### '+section)
            table=model.grid(saved['rows'],labels,years)/1e8
            display=table.map(lambda value:'—' if pd.isna(value) else f'{value:,.1f}')
            st.dataframe(display.style.set_properties(**{'color':palette['text'],'background-color':palette['surface']}),width='stretch',
                         height=min(390,38+len(labels)*35))
        st.markdown('#### 핵심 모델링 지표')
        table=model.grid(saved['rows'],model.RATIOS,years,derived=True)
        table.loc['FCF (유형자산 기준)']/=1e8
        display=table.copy().astype(object)
        for label in table.index:
            for col in table.columns:
                v=table.loc[label,col]
                display.loc[label,col]='—' if pd.isna(v) else (f'{v:,.1f}억' if label.startswith('FCF') else f'{v:.1%}')
        st.dataframe(display.style.set_properties(**{'color':palette['text'],'background-color':palette['surface']}),width='stretch',height=320)
        with st.expander('추이 그래프'):
            shown=financials[financials.연도.isin(years)].copy()
            choices=st.multiselect('비교 계정',list(src.ACCOUNTS),default=['매출액','영업이익'])
            parts=[]
            for label in choices:
                f=shown[['연도',label]].dropna().rename(columns={label:'value'})
                f['date']=pd.to_datetime(f.연도.astype(str)+'-12-31');f['value']/=1e8;f['series']=label;parts.append(f)
            if parts and any(not f.empty for f in parts):
                st.altair_chart(chart_ui.timeseries(pd.concat(parts),'date','value','억 원',group='series',domain=(pd.Timestamp(years[0],1,1),pd.Timestamp(years[-1],12,31))),use_container_width=True,theme=None)
                combined=pd.concat(parts)
                scales=combined.groupby('series').value.apply(lambda v:v.abs().median())
                scales=scales[scales>0]
                if len(scales)>1 and scales.max()/scales.min()>=20:
                    from comparison_engine import transform
                    names=combined.groupby('series').value.first()
                    eligible=names[names>0].index
                    if len(eligible)>1:
                        st.caption('시작값 = 100 · 수치 규모가 다른 계정의 추이 비교')
                        trend=transform(combined[combined.series.isin(eligible)],'시작값 = 100')
                        st.altair_chart(chart_ui.timeseries(trend,'date','value','시작값 100',group='series',domain=(pd.Timestamp(years[0],1,1),pd.Timestamp(years[-1],12,31))),width='stretch',theme=None)
        with st.expander('계산 기준 · 누락 항목 · 원문'):
            st.caption('ROE는 총당기순이익 ÷ 전년·당년 평균 총자본이며 지배주주 ROE와 다릅니다. 영업이익률·순이익률은 매출액 기준, 부채비율은 부채 ÷ 자본입니다. 계정 ID를 우선 사용하며 모호한 항목은 공란으로 표시합니다. 금융업 등 업종에 따라 단순 비율 비교는 제한됩니다. TTM·정상화 이익·주가 기반 가치평가는 포함하지 않습니다.')
            for note in saved['warnings']:st.caption(note)
            for row in saved['rows']:
                if row.get('접수번호'):st.markdown(f"[{row['연도']}년 사업보고서](https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['접수번호']})")
        st.subheader('최근 공시')
        if st.button('최근 공시 불러오기'):
            with st.spinner('최근 공시 조회 중…'):
                try:
                    saved['notices']=src.dart_disclosures(company['corp_code'],(date.today()-timedelta(days=365)).strftime('%Y%m%d'),date.today().strftime('%Y%m%d'),key)
                    saved['notices_loaded']=True
                except src.SourceError as exc:st.warning(str(exc))
        if saved.get('notices_loaded') and not saved['notices']:st.caption('최근 1년 공시가 없습니다.')
        for notice in saved['notices']:
            receipt=notice.get('rcept_no','')
            if receipt.isdigit():st.markdown('['+escape(notice.get('report_nm','공시'))+'](https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+receipt+') · '+notice.get('rcept_dt',''))
    except src.SourceError as exc:st.error(str(exc))
