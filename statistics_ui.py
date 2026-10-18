"""KOSIS discovery and series-level descriptive analysis."""
from datetime import date
import pandas as pd
import streamlit as st
import api_settings
import analysis_sources as src
import chart_ui

TOPICS=['소비자물가지수','고용률 실업률','산업생산지수','소매판매액지수','인구','출생 사망','주택가격','가계소득','수출 수입','설비투자','건설수주']

def render():
    st.subheader('통계 데이터')
    key=api_settings.read_key('KOSIS')
    if not key:
        st.info('관리자가 KOSIS 인증키를 등록하면 주요 통계를 조회할 수 있습니다.')
        st.markdown('[관리자 API 설정](/settings) · [KOSIS 키 발급](https://kosis.kr/openapi/)')
        st.write('수집 주제: '+ ' · '.join(TOPICS));return
    left,right=st.columns([2,3])
    topic=left.selectbox('주요 통계',TOPICS)
    query=right.text_input('통계 검색',value=topic,key='kosis_query_'+topic)
    try:
        tables=src.kosis_search(query,key)
        if not tables:st.info('검색된 통계표가 없습니다.');return
        choices={r['ORG_ID']+'/'+r['TBL_ID']:r for r in tables}
        chosen=st.selectbox('통계표',list(choices),format_func=lambda k:choices[k]['TBL_NM']+' · '+choices[k].get('ORG_NM',''))
        table=choices[chosen]
        inferred='Y' if len(str(table.get('END_PRD_DE','')))==4 else 'M'
        freq=st.selectbox('수록 주기',['M','Q','Y'],index=['M','Q','Y'].index(inferred),format_func=lambda x:{'M':'월간','Q':'분기','Y':'연간'}[x])
        sample=src.parse_kosis(src.kosis_rows(table['ORG_ID'],table['TBL_ID'],freq,1,{},key))
        if sample.empty:st.info('이 주기의 수치가 없습니다. 다른 수록 주기를 선택해주세요.');return
        specs=sample.drop_duplicates('series').set_index('series')
        series=st.selectbox('분석할 항목·지역·분류',list(specs.index),format_func=lambda k:specs.loc[k,'label']+' · '+str(specs.loc[k,'unit']))
        count=st.select_slider('최근 관측 수',[12,24,36,60,120],value=60)
        selected=specs.loc[series]
        raw=src.kosis_rows(table['ORG_ID'],table['TBL_ID'],freq,count,selected['filters'],key)
        all_rows=src.parse_kosis(raw)
        f=all_rows[all_rows.series==series].sort_values('date') if not all_rows.empty else pd.DataFrame()
        if f.empty:st.info('선택 조건에 맞는 수치가 없습니다.');return
        dates=st.date_input('분석 기간',(f.date.min().date(),f.date.max().date()),min_value=f.date.min().date(),max_value=f.date.max().date())
        if len(dates)!=2:return
        f=f[f.date.between(pd.Timestamp(dates[0]),pd.Timestamp(dates[1]))]
        stats=src.summary(f)
        if not stats:st.info('분석 구간의 관측값이 없습니다.');return
        unit=str(selected['unit']);a,b,c,d=st.columns(4)
        a.metric('최신값 · '+unit,f"{stats['latest']:,.2f}")
        b.metric('직전 관측 대비', '—' if stats['delta'] is None else f"{stats['delta']:+,.2f}",None if stats['pct'] is None else f"{stats['pct']:+.2f}%",delta_color='off')
        c.metric('기간 최고',f"{stats['high']['value']:,.2f}");c.caption(stats['high']['date'].strftime('%Y-%m'))
        d.metric('기간 최저',f"{stats['low']['value']:,.2f}");d.caption(stats['low']['date'].strftime('%Y-%m'))
        st.altair_chart(chart_ui.timeseries(f,'date','value',unit,domain=dates),use_container_width=True,theme=None)
        name='KOSIS / '+table['TBL_NM']+' / '+selected['label']+' / '+freq
        url='https://kosis.kr/statHtml/statHtml.do?orgId='+table['ORG_ID']+'&tblId='+table['TBL_ID']
        if st.button('데이터 비교에 추가',key='kosis_add'):
            entries=st.session_state.setdefault('external_series',{})
            entries[name]={'frame':f[['date','value']].copy(),'unit':unit,'meta':{'url':url}}
            choices=list(st.session_state.get('comparison_choices',[]))
            if name not in choices:choices.append(name)
            st.session_state['comparison_choices']=choices;st.session_state['comparison_selection']=choices[:]
            st.success('비교 목록에 추가했습니다.')
        st.markdown('[원자료 통계표]('+url+') · [데이터 비교](/compare)')
        with st.expander('관측값 · 계산 기준'):
            st.dataframe(f[['period','value','unit']].rename(columns={'period':'관측기간','value':'값','unit':'단위'}),hide_index=True,use_container_width=True)
            st.caption('최고·최저는 선택 구간 기준입니다. 증감률은 직전 값이 양수일 때만 계산하며, 비율 지표의 차이는 원단위 차이입니다. 월·분기 날짜는 관측기간 시작일이며 발표일이 아닙니다. 누락·비공개 값은 0으로 바꾸지 않습니다.')
    except src.SourceError as exc:st.error(str(exc))
