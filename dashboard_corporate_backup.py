"""종목코드로 재무 데이터를 조회하는 로컬 대시보드."""
import json
from datetime import datetime
from pathlib import Path

import httpx
import streamlit as st
from keyring.backends.macOS import Keyring
import dart_financials as dart
from valuation import fetch_market, metrics

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'
st.set_page_config(page_title='기업 가치 리서치', page_icon='📊', layout='wide')
st.title('기업 가치 리서치')
st.caption('DART 재무제표와 시장 데이터를 확인하고 비교 분석을 준비합니다.')

with st.sidebar:
    st.header('분석 설정')
    code = st.text_input('보통주 종목코드', placeholder='예: 005930', max_chars=6)
    year = st.number_input('사업연도', min_value=2015, max_value=datetime.now().year,
                           value=datetime.now().year - 1, step=1)
    refresh = st.checkbox('DART 자료 새로고침', value=False)
    market_enabled = st.checkbox('주가·시장 데이터도 조회', value=True)
    with st.expander('DART 인증키 등록·교체'):
        st.caption('입력한 키는 조회 성공 후 Mac 키체인에 저장합니다. 결과 파일에는 포함하지 않습니다.')
        key_input = st.text_input('DART API 키', type='password', key='dart_key')
    run = st.button('분석 시작', type='primary', use_container_width=True)

if run:
    if len(code) != 6 or not code.isascii() or not code.isdigit():
        st.error('종목코드를 숫자 6자리로 입력해주세요.')
    else:
        try:
            with st.spinner('기업과 재무 데이터를 확인하고 있습니다…'):
                RESULTS.mkdir(exist_ok=True)
                cached = dart.load_cached(RESULTS, code, str(year))
                if cached and not refresh:
                    payload, _ = cached
                    cached_used = True
                else:
                    vault = Keyring()
                    try:
                        key = key_input.strip() or vault.get_password('research-agent-learning.dart', 'api-key')
                    except Exception:
                        key = key_input.strip()
                    if not key:
                        raise dart.DartError('왼쪽 인증키 등록 항목에 DART 키를 입력해주세요.')
                    with httpx.Client(timeout=60, follow_redirects=False) as client:
                        company = dart.find_company(dart.get_data(client, 'corpCode.xml', key), code)
                        division, data = dart.fetch_statements(client, key, company, str(year))
                    receipt = data['list'][0].get('rcept_no', '')
                    payload = {'company': company, 'year': str(year), 'report_code': '11011',
                               'fs_div': division, 'retrieved_at': datetime.now().astimezone().isoformat(),
                               'source_url': f'https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt}',
                               'response': data}
                    path = RESULTS / f'dart_{code}_{year}_{datetime.now():%Y%m%d_%H%M%S_%f}.json'
                    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
                    if key_input.strip():
                        try:
                            vault.set_password('research-agent-learning.dart', 'api-key', key)
                        except Exception:
                            st.warning('조회는 성공했으나 키체인 저장은 실패했습니다.')
                    cached_used = False
                st.session_state['analysis'] = {'payload': payload, 'cached': cached_used,
                                                'market': None, 'market_error': None}
            if market_enabled:
                with st.spinner('시장 데이터를 조회하고 있습니다…'):
                    try:
                        st.session_state['analysis']['market'] = fetch_market(code)
                    except Exception:
                        st.session_state['analysis']['market_error'] = '시장 조회 실패. 재무제표는 아래에서 확인할 수 있습니다.'
        except dart.DartError as error:
            st.error(str(error))
        except Exception:
            st.error('조회 또는 저장에 실패했습니다. 인증키·네트워크·DART 서비스 상태를 확인해주세요.')

analysis = st.session_state.get('analysis')
if not analysis:
    st.info('왼쪽에서 종목코드를 입력하고 분석 시작을 눌러주세요.')
    st.stop()
p = analysis['payload']
m = analysis['market']
st.subheader(f"{p['company']['corp_name']} · {p['company']['stock_code']}")
st.caption(f"{p['year']} 연간 / {'연결' if p['fs_div']=='CFS' else '별도'} / 조회일 {p['retrieved_at']} / "
           + ('저장 자료 사용' if analysis['cached'] else 'DART 새로 조회'))
st.markdown(f"[DART 원문 공시]({p['source_url']})")
summary, peers, normalized, risks, shares = st.tabs(['재무 요약', '피어 비교', '정상화 이익', '주석 리스크', '주식 구조'])
with summary:
    if analysis['market_error']:
        st.warning(analysis['market_error'])
    if m:
        st.metric('조회 가격', f"{m['price']:,.0f}원")
        st.caption(f"시장 시각: {m['quote_time']} · Yahoo Finance · 실시간 보장 없음")
    values = metrics(p, m or {'price': None, 'book_value': None})
    columns = st.columns(4)
    for col, label, field, suffix in zip(columns,
        ['연간 PER', 'PBR · Yahoo BPS 기준', '연간 ROE', '영업이익률'],
        ['PER_annual', 'PBR_provider_bps', 'ROE_annual_percent', 'operating_margin_percent'],
        ['배','배','%','%']):
        value = values[field]
        col.metric(label, '산출 불가' if value is None else f'{value:,.2f}{suffix}')
    st.caption('PER는 선택 연도 기본 EPS 기준입니다. PBR는 Yahoo BPS 기반으로 재무기간이 다를 수 있습니다. TTM·피어 비교용 확정 지표가 아닙니다.')
    if m:
        st.markdown(f"[시장 데이터 출처]({m['source']})")
    with st.expander('재무제표 계정과 원본 확인'):
        rows = [{k:r.get(k,'') for k in ['sj_nm','account_id','account_nm','thstrm_nm','thstrm_amount','frmtrm_amount','currency']}
                for r in p['response']['list']]
        st.dataframe(rows, use_container_width=True)
    st.download_button('재무 데이터 다운로드', json.dumps(p, ensure_ascii=False, indent=2),
                       file_name=f"dart_{p['company']['stock_code']}_{p['year']}.json", mime='application/json')
with peers:
    st.info('구현 예정: 공시 사업 내용을 검색해 유사 기업 최대 4곳을 선정하고 원문 근거와 지표를 비교합니다.')
with normalized:
    st.info('구현 예정: 일회성 손익 후보와 근거를 제안하고, 사용자가 승인한 조정만 계산에 반영합니다.')
with risks:
    st.info('구현 예정: 주석·경영진단에서 확인되는 리스크를 최대 3개까지 근거와 함께 표시합니다.')
with shares:
    st.info('구현 예정: 동일 발행사의 보통주·우선주를 확인해 가격 괴리와 시가총액 구성을 비교합니다.')
    if m and m.get('market_cap_provider'):
        st.metric('Yahoo 제공 시가총액', f"{m['market_cap_provider']:,.0f}원")
        st.caption('보통주·우선주 포함 범위가 검증되지 않아 가치 계산에 사용하지 않습니다.')
