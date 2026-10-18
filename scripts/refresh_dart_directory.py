"""Build a public company-code snapshot from DART's official company search.

No API key is required. Resumes an existing snapshot; no keys or URLs with keys
are saved. KRX supplies the listed-company universe, DART supplies corp_code.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis_sources import parse_dart_search
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'static/dart-companies.json')
    args = parser.parse_args()
    companies = json.loads((ROOT / 'static/krx-companies.json').read_text())['companies']
    saved = json.loads(args.output.read_text()) if args.output.exists() else {'companies': []}
    found = {c['stock_code']: c for c in saved['companies']}
    pending = [c for c in companies if c['stock_code'] not in found]
    failures = []
    with httpx.Client(timeout=httpx.Timeout(10, connect=4), limits=httpx.Limits(max_connections=4)) as client:
        def lookup(company):
            response = client.post('https://dart.fss.or.kr/dsae001/search.ax', data={
                'textCrpNm': company['stock_code'], 'currentPage': '1', 'maxResults': '100'})
            response.raise_for_status()
            return next((r for r in parse_dart_search(response.text)
                         if r['stock_code'] == company['stock_code']), None)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(lookup, c): c for c in pending}
            for i, future in enumerate(as_completed(futures), 1):
                company = futures[future]
                try:
                    row = future.result()
                    if row:found[row['stock_code']] = row
                    else:failures.append(company['stock_code'])
                except Exception:failures.append(company['stock_code'])
                if i % 100 == 0:print(f'{i}/{len(pending)} checked; {len(found)} resolved', flush=True)
    payload = {'source': 'https://dart.fss.or.kr/dsae001/search.ax',
               'universe_source': 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13',
               'retrieved_at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
               'companies': sorted(found.values(), key=lambda c:c['stock_code']),
               'unresolved_stock_codes': sorted(failures)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
    print(f'Saved {len(found)} company codes; unresolved {len(failures)}', flush=True)
    return 0 if found else 1


if __name__ == '__main__':raise SystemExit(main())
