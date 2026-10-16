"""DART 연간 실적과 Yahoo 시장 데이터를 함께 점검하는 첫 버전."""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import yfinance as yf
import dart_financials as dart


def number(value):
    try:
        n = float(str(value).replace(',', '').strip())
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def account(rows, ids, statements, field='thstrm_amount'):
    candidates = [r for r in rows if r.get('account_id') in ids
                  and r.get('sj_div') in statements and r.get('currency') == 'KRW']
    values = {number(r.get(field)) for r in candidates}
    values.discard(None)
    # 충돌하는 계정은 임의 선택하지 않습니다.
    return next(iter(values)) if len(values) == 1 else None


def ratio(n, d):
    return n / d if n is not None and d is not None and d > 0 else None


def metrics(payload, market):
    rows = payload['response']['list']
    income = ('IS', 'CIS')
    revenue = account(rows, {'ifrs-full_Revenue'}, income)
    operating = account(rows, {'dart_OperatingIncomeLoss'}, income)
    parent = payload['fs_div'] == 'CFS'
    profit_ids = {'ifrs-full_ProfitLossAttributableToOwnersOfParent'} if parent else {'ifrs-full_ProfitLoss'}
    equity_ids = {'ifrs-full_EquityAttributableToOwnersOfParent'} if parent else {'ifrs-full_Equity'}
    profit = account(rows, profit_ids, income)
    equity = account(rows, equity_ids, ('BS',))
    previous_equity = account(rows, equity_ids, ('BS',), 'frmtrm_amount')
    average_equity = ((equity + previous_equity) / 2
                      if equity is not None and previous_equity is not None else None)
    eps = account(rows, {'ifrs-full_BasicEarningsLossPerShare'}, income)
    return {'revenue': revenue, 'operating_profit': operating,
            'profit': profit, 'equity': equity, 'average_equity': average_equity,
            'annual_basic_eps': eps,
            'PER_annual': ratio(market['price'], eps),
            'PBR_provider_bps': ratio(market['price'], market.get('book_value')),
            'ROE_annual_percent': (ratio(profit, average_equity) * 100
                                   if ratio(profit, average_equity) is not None else None),
            'operating_margin_percent': (ratio(operating, revenue) * 100
                                          if ratio(operating, revenue) is not None else None)}


def fetch_market(code):
    # 코스피와 코스닥을 순서대로 확인합니다.
    for suffix in ('.KS', '.KQ'):
        symbol = code + suffix
        try:
            info = yf.Ticker(symbol).get_info()
            price = number(info.get('regularMarketPrice'))
            timestamp = number(info.get('regularMarketTime'))
            if info.get('currency') != 'KRW' or not price or not timestamp:
                continue
            return {'symbol': symbol, 'price': price,
                    'quote_time': datetime.fromtimestamp(timestamp, ZoneInfo('Asia/Seoul')).isoformat(),
                    'market_cap_provider': number(info.get('marketCap')),
                    'book_value': number(info.get('bookValue')),
                    'provider_financial_period': info.get('mostRecentQuarter'),
                    'source': f'https://finance.yahoo.com/quote/{symbol}/',
                    'retrieved_at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat()}
        except Exception:
            continue
    raise ValueError('시장 데이터를 조회하지 못했습니다. 잠시 후 다시 실행하세요. 재무제표는 저장돼 있습니다.')


def main():
    payload = dart.main()
    if not payload:
        return
    print('\n주가·시장 데이터 조회 중…')
    try:
        market = fetch_market(payload['company']['stock_code'])
    except ValueError as error:
        print(error)
        return
    result = metrics(payload, market)
    lines = [f"# {payload['company']['corp_name']} 밸류에이션 점검",
             f"재무 기준: {payload['year']} 사업보고서 / {payload['fs_div']}",
             f"주가 시각(한국): {market['quote_time']}",
             f"조회 가격: {market['price']:,.0f}원 (실시간 보장 없음)"]
    if market['market_cap_provider']:
        lines.append(f"Yahoo 제공 시가총액: {market['market_cap_provider']:,.0f}원 — 보통주·우선주 포함 범위 미검증, 계산에 사용하지 않음")
    for label, key, unit in [
        ('연간 기본 EPS', 'annual_basic_eps', '원'),
        ('PER (선택 연도 기본 EPS 기준)', 'PER_annual', '배'),
        ('PBR (Yahoo 제공 BPS 기준)', 'PBR_provider_bps', '배'),
        ('ROE (연간 순이익 / 기초·기말 평균자본)', 'ROE_annual_percent', '%'),
        ('영업이익률', 'operating_margin_percent', '%')]:
        value = result[key]
        lines.append(f"{label}: {value:,.2f}{unit}" if value is not None
                     else f"{label}: 산출 불가 (누락·계정 충돌 또는 분모가 0 이하)")
    period = market.get('provider_financial_period')
    if period:
        lines.append('Yahoo 재무 기준일: ' + datetime.fromtimestamp(period, ZoneInfo('Asia/Seoul')).date().isoformat())
    lines.extend([
        'PER는 DART 연간 기본 EPS 기반이며 TTM·예상 PER가 아닙니다.',
        'PBR는 Yahoo 제공 BPS를 사용합니다. DART 연간 자본 기반 PBR와 기간·주식수 기준이 다를 수 있습니다.',
        '연결이면 ROE는 지배주주 순이익·자본, 별도이면 순이익·자본 기준입니다.',
        '우선주가 있는 기업은 보통주 EPS 배분을 원문에서 확인해야 합니다. 주식분할 등 발생 시 과거 EPS와 현재 주가 비교가 부적합할 수 있습니다.',
        '현재 버전은 지표 점검용입니다. 비교기업 분석·적정주가·AI 설명은 아직 포함하지 않습니다.',
        'DART 출처: ' + payload['source_url'], '시장 데이터 출처: ' + market['source']])
    folder = Path(__file__).resolve().parent / 'results'
    stem = f"valuation_{payload['company']['stock_code']}_{datetime.now():%Y%m%d_%H%M%S_%f}"
    report = folder / (stem + '.md')
    report.write_text('\n\n'.join(lines), encoding='utf-8')
    (folder / (stem + '.json')).write_text(json.dumps(
        {'financials': payload, 'market': market, 'metrics': result}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n' + '\n'.join(lines))
    print(f'\n보고서 저장: {report}')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\n종료했습니다.')
