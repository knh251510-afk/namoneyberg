"""DART annual financial analysis and disclosures, without LLM-generated figures."""
from datetime import date,timedelta
from html import escape
import pandas as pd
import streamlit as st
import api_settings
import analysis_sources as src
import chart_ui
import financial_model as model

def render():
    st.caption('공시 기반 재무제표 · 모델링 기초 데이터')
    key=api_settings.read_key('DART')
    if not key:
        st.info('관리자가 DART 인증키를 등록하면 기업 재무제표와 공시를 조회할 수 있습니다.')
        st.markdown('[관리자 API 설정](/settings) · [DART 키 발급](https://opendart.fss.or.kr/)');return
    try:
        companies=src.dart_companies(key)
        query=st.text_input('기업명 또는 종목코드',placeholder='예: 삼성전자 또는 005930')
        matched=[c for c in companies if query.strip() and (query.strip() in c['name'] or query.strip() in c['stock_code'])][:100]
        if not matched:st.info('기업명 또는 6자리 종목코드를 입력해주세요.');return
        selected=st.selectbox('기업 선택',range(len(matched)),format_func=lambda i:matched[i]['name']+' · '+matched[i]['stock_code'])
        company=matched[selected]
        a,b,c=st.columns(3)
        year=a.number_input('사업연도',min_value=2015,max_value=date.today().year,value=date.today().year-1,step=1)
        basis=b.selectbox('재무제표',['CFS','OFS'],format_func=lambda x:'연결' if x=='CFS' else '별도')
        span=c.selectbox('비교 연수',[3,5],index=0)
        if st.button('재무분석 조회',type='primary'):
            frames=[];warnings=[];raw={}
            with st.spinner('DART 재무제표와 공시 조회 중…'):
                for y in range(max(2015,year-span),year+1):
                    rows=src.dart_statement(company['corp_code'],int(y),basis,key);raw[y]=rows
                    if not rows:warnings.append(str(y)+'년 자료 없음');continue
                    values=src.extract_financials(rows);frames.append({'연도':y,**values})
                    if values['누락·모호']:warnings.append(str(y)+'년 확인 필요: '+', '.join(values['누락·모호']))
                notices=src.dart_disclosures(company['corp_code'],(date.today()-timedelta(days=365)).strftime('%Y%m%d'),date.today().strftime('%Y%m%d'),key)
            st.session_state['corporate_result']={'identity':(company['corp_code'],int(year),basis,span),'company':company,'rows':frames,'raw':raw,'notices':notices,'warnings':warnings}
        saved=st.session_state.get('corporate_result')
        if not saved or saved['identity']!=(company['corp_code'],int(year),basis,span):return
        financials=pd.DataFrame(saved['rows'])
        if financials.empty:st.info('선택한 기준의 연간 재무제표가 없습니다. 연도나 연결·별도를 변경해주세요.');return
        financials=financials.sort_values('연도');latest=financials[financials.연도==year]
        if latest.empty:st.warning('선택 연도 자료가 없습니다. 과거 자료만 표시합니다.')
        st.caption(company['name']+' · '+('연결' if basis=='CFS' else '별도')+' · 연간 사업보고서 · 금액 KRW, 표시 단위 억 원')
        years=list(range(int(year)-span+1,int(year)+1))
        st.download_button('엑셀 다운로드',model.export_xlsx(saved,years,basis),
                           file_name=company['stock_code']+'_fundamentals_'+basis+'.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.caption('열: 사업연도 · 행: 재무 계정 · 미제공·모호한 값은 — · 예측 전 단계의 과거 실적')
        for section,labels in model.SECTIONS.items():
            st.markdown('#### '+section)
            table=model.grid(saved['rows'],labels,years)/1e8
            st.dataframe(table.style.format('{:,.1f}',na_rep='—'),use_container_width=True,
                         height=min(390,38+len(labels)*35))
        st.markdown('#### 핵심 모델링 지표')
        table=model.grid(saved['rows'],model.RATIOS,years,derived=True)
        table.loc['FCF (유형자산 기준)']/=1e8
        display=table.copy().astype(object)
        for label in table.index:
            for col in table.columns:
                v=table.loc[label,col]
                display.loc[label,col]='—' if pd.isna(v) else (f'{v:,.1f}억' if label.startswith('FCF') else f'{v:.1%}')
        st.dataframe(display,use_container_width=True,height=320)
        with st.expander('추이 그래프'):
            shown=financials[financials.연도.isin(years)].copy()
            choices=st.multiselect('비교 계정',list(src.ACCOUNTS),default=['매출액','영업이익'])
            parts=[]
            for label in choices:
                f=shown[['연도',label]].dropna().rename(columns={label:'value'})
                f['date']=pd.to_datetime(f.연도.astype(str)+'-12-31');f['value']/=1e8;f['series']=label;parts.append(f)
            if parts and any(not f.empty for f in parts):
                st.altair_chart(chart_ui.timeseries(pd.concat(parts),'date','value','억 원',group='series',domain=(pd.Timestamp(years[0],1,1),pd.Timestamp(years[-1],12,31))),use_container_width=True,theme=None)
        with st.expander('계산 기준 · 누락 항목 · 원문'):
            st.caption('ROE는 총당기순이익 ÷ 전년·당년 평균 총자본이며 지배주주 ROE와 다릅니다. 영업이익률·순이익률은 매출액 기준, 부채비율은 부채 ÷ 자본입니다. 계정 ID를 우선 사용하며 모호한 항목은 공란으로 표시합니다. 금융업 등 업종에 따라 단순 비율 비교는 제한됩니다. TTM·정상화 이익·주가 기반 가치평가는 포함하지 않습니다.')
            for note in saved['warnings']:st.caption(note)
            for row in saved['rows']:
                if row.get('접수번호'):st.markdown(f"[{row['연도']}년 사업보고서](https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['접수번호']})")
        st.subheader('최근 공시')
        for notice in saved['notices']:
            receipt=notice.get('rcept_no','')
            if receipt.isdigit():st.markdown('['+escape(notice.get('report_nm','공시'))+'](https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+receipt+') · '+notice.get('rcept_dt',''))
    except src.SourceError as exc:st.error(str(exc))
