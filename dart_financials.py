"""종목코드로 DART 기업을 찾고 지정 연도 재무제표를 조회합니다."""
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from getpass import getpass
from pathlib import Path

import httpx

from keyring.backends.macOS import Keyring

BASE = 'https://opendart.fss.or.kr/api/'


class DartError(Exception):
    pass


def get_data(client, endpoint, key, **params):
    try:
        response = client.get(BASE + endpoint, params={'crtfc_key': key, **params})
        response.raise_for_status()
        return response.content
    except httpx.HTTPError:
        # URL에는 인증키가 있으므로 예외 원문을 출력하지 않습니다.
        raise DartError('DART 연결 실패. 인터넷 연결 또는 서비스 상태를 확인하세요.') from None


def find_company(content, stock_code):
    if not zipfile.is_zipfile(io.BytesIO(content)):
        try:
            root = ET.fromstring(content)
            status = root.findtext('status', '알 수 없음')
        except ET.ParseError:
            status = '응답 형식 오류'
        raise DartError(f'기업 목록 조회 실패: {status}. 인증키 활성화 여부를 확인하세요.')
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith('.xml'))
        root = ET.fromstring(archive.read(name))
    matches = [item for item in root.findall('list')
               if (item.findtext('stock_code') or '').strip() == stock_code]
    if len(matches) != 1:
        raise DartError('해당 종목코드를 찾지 못했거나 기업을 특정할 수 없습니다. 보통주 종목코드를 확인하세요.')
    item = matches[0]
    return {'corp_code': item.findtext('corp_code'),
            'corp_name': item.findtext('corp_name'), 'stock_code': stock_code}


def fetch_statements(client, key, company, year):
    for division in ('CFS', 'OFS'):
        raw = get_data(client, 'fnlttSinglAcntAll.json', key,
                       corp_code=company['corp_code'], bsns_year=year,
                       reprt_code='11011', fs_div=division)
        data = json.loads(raw)
        if data.get('status') == '000' and data.get('list'):
            return division, data
        if data.get('status') != '013':
            raise DartError(f"재무제표 조회 실패: DART 상태 {data.get('status', '알 수 없음')}")
        if division == 'CFS':
            print('연결 자료 없음 → 별도 재무제표 조회')
    raise DartError('지정 연도 사업보고서 자료가 없습니다. 다른 사업연도를 선택하세요.')


def load_cached(folder, stock_code, year):
    for path in sorted(folder.glob(f'dart_{stock_code}_{year}_*.json'), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
            if (payload['company']['stock_code'] == stock_code
                    and str(payload['year']) == year
                    and payload['report_code'] == '11011'
                    and payload['fs_div'] in ('CFS', 'OFS')
                    and payload['response']['status'] == '000'
                    and payload['response']['list']):
                return payload, path
        except (ValueError, KeyError, TypeError, OSError):
            continue
    return None


def get_key(reset=False):
    vault = Keyring()  # 다른 저장소 대신 Mac 키체인을 직접 사용합니다.
    service, account = 'research-agent-learning.dart', 'api-key'
    if not reset:
        try:
            existing = vault.get_password(service, account)
            if existing:
                print('Mac 키체인에서 DART 키를 불러왔습니다.')
                return existing, False
        except Exception:
            print('키체인을 읽지 못했습니다. 이번 실행에 사용할 키를 입력해주세요.')
    key = getpass('DART API 키 입력 (화면에 표시되지 않음): ').strip()
    return key, True


def save_key(key):
    try:
        Keyring().set_password('research-agent-learning.dart', 'api-key', key)
        print('DART 키를 Mac 키체인에 저장했습니다. 다음부터 자동으로 불러옵니다.')
    except Exception:
        print('키체인 저장에 실패했습니다. 이번 조회는 완료했으며 다음 실행 시 다시 입력해야 합니다.')


def main():
    print('DART 재무제표 조회 — 현재 단계는 주가·적정가치 계산 전입니다.')
    stock_code = input('보통주 종목코드 6자리: ').strip()
    if not re.fullmatch(r'[0-9]{6}', stock_code):
        print('종목코드는 앞의 0을 포함한 숫자 6자리로 입력하세요.')
        return
    default_year = datetime.now().year - 1
    year = input(f'사업연도 [Enter: {default_year}]: ').strip() or str(default_year)
    if not re.fullmatch(r'[0-9]{4}', year) or not 2015 <= int(year) <= datetime.now().year:
        print('사업연도는 2015년부터 현재 연도까지 입력하세요.')
        return
    folder = Path(__file__).resolve().parent / 'results'
    folder.mkdir(exist_ok=True)
    cached = load_cached(folder, stock_code, year)
    use_cache = False
    if cached:
        payload, path = cached
        print(f"저장된 자료: {payload['company']['corp_name']} / 조회일 {payload.get('retrieved_at', '미상')}")
        use_cache = input('Enter: 저장 자료 사용 / r: DART 새로고침: ').strip().lower() != 'r'
    if use_cache:
        company, division, data = payload['company'], payload['fs_div'], payload['response']
        print('저장 자료를 사용합니다. DART에 접속하지 않습니다.')
    else:
        reset = input('Enter: 저장된 키 사용 / k: 키 등록·교체: ').strip().lower() == 'k'
        key, new_key = get_key(reset)
        if not key:
            print('키를 입력해주세요.')
            return
        try:
            with httpx.Client(timeout=60, follow_redirects=False) as client:
                print('기업 목록 조회 중…')
                company = find_company(get_data(client, 'corpCode.xml', key), stock_code)
                print(f"기업: {company['corp_name']} ({stock_code})")
                division, data = fetch_statements(client, key, company, year)
        except DartError as error:
            print(error)
            return
        except (ValueError, ET.ParseError, zipfile.BadZipFile, StopIteration):
            print('DART 응답을 해석하지 못했습니다. 잠시 후 다시 시도하세요.')
            return
        if new_key:
            save_key(key)

    rows = data['list']
    print(f"\n{year} 사업보고서 / {'연결' if division == 'CFS' else '별도'} / {len(rows)}개 계정")
    names = {'매출액', '수익(매출액)', '영업이익', '영업이익(손실)',
             '당기순이익', '당기순이익(손실)', '자산총계', '부채총계', '자본총계'}
    ids = {'ifrs-full_Revenue', 'dart_OperatingIncomeLoss', 'ifrs-full_ProfitLoss',
           'ifrs-full_Assets', 'ifrs-full_Liabilities', 'ifrs-full_Equity',
           'ifrs-full_ProfitLossAttributableToOwnersOfParent',
           'ifrs-full_EquityAttributableToOwnersOfParent'}
    shown = set()
    for row in rows:
        identity = (row.get('account_id'), row.get('account_nm'))
        if row.get('sj_div') not in ('BS', 'IS', 'CIS') or identity in shown:
            continue
        if row.get('account_id') in ids or row.get('account_nm') in names:
            shown.add(identity)
            print(f"{row.get('account_nm')}: {row.get('thstrm_amount') or '값 없음'} {row.get('currency', '')} ({row.get('thstrm_nm', '')})")
    if not shown:
        print('표준 주요계정과 일치하는 항목이 없습니다. 저장된 원본에서 계정 확인이 필요합니다.')
    receipt = rows[0].get('rcept_no', '')
    source_url = f'https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt}'
    if not use_cache:
        path = folder / f'dart_{stock_code}_{year}_{datetime.now():%Y%m%d_%H%M%S_%f}.json'
        payload = {'company': company, 'year': year, 'report_code': '11011',
                   'fs_div': division, 'retrieved_at': datetime.now().astimezone().isoformat(),
                   'source_url': source_url, 'response': data}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n원문 공시: {source_url}')
    print(f'전체 재무제표 저장: {path}')
    print('결과 파일에 키는 포함되지 않습니다. 지정 연도 연간 자료이며 최신 분기·TTM 자료가 아닙니다.')
    return payload


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\n입력을 종료했습니다.')
