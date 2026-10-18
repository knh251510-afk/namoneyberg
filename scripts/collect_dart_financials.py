"""Collect official annual statements using DART_API_KEY from the environment."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo
import httpx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dart_storage import write_snapshot


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--companies',default='005930,000660,006400,005380,035420')
    parser.add_argument('--year',type=int,default=datetime.now().year-1)
    parser.add_argument('--span',type=int,choices=[3,5],default=3)
    parser.add_argument('--basis',choices=['CFS','OFS','both'],default='both')
    parser.add_argument('--output',type=Path,default=ROOT/'macro_cache/dart')
    parser.add_argument('--use-keychain',action='store_true',help='Use the existing local DART key (run with the original local Python).')
    args=parser.parse_args()
    key=os.environ.get('DART_API_KEY','').strip()
    if not key and args.use_keychain:
        import api_settings
        key=(api_settings.read_key('DART') or '').strip()
    if not key:
        print('DART_API_KEY secret is missing. Add it in repository Actions secrets.',file=sys.stderr)
        return 2
    directory=json.loads((ROOT/'static/dart-companies.json').read_text())['companies']
    wanted=[v.strip() for v in args.companies.split(',') if v.strip()]
    lookup={c['stock_code']:c for c in directory}
    if not wanted or len(wanted)>30 or any(v not in lookup for v in wanted):
        print('Select 1–30 valid listed stock codes from static/dart-companies.json.',file=sys.stderr)
        return 2
    tasks=[(lookup[stock]['corp_code'],y,basis) for stock in wanted
           for y in range(max(2015,args.year-args.span),args.year+1)
           for basis in (['CFS','OFS'] if args.basis=='both' else [args.basis])]
    ok=0;empty=0;failed=0
    with httpx.Client(timeout=httpx.Timeout(25,connect=5),limits=httpx.Limits(max_connections=3)) as client:
        def collect(task):
            corp,year,basis=task
            try:
                response=client.get('https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json',params={'crtfc_key':key,'corp_code':corp,'bsns_year':year,'reprt_code':'11011','fs_div':basis})
                response.raise_for_status();payload=response.json();status=payload.get('status')
                if status=='013':return 'empty'
                if status!='000':return 'DART status '+str(status)
                write_snapshot(args.output,corp,year,basis,payload.get('list',[]),datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'))
                return 'ok'
            except httpx.TimeoutException:return 'timeout'
            except (httpx.HTTPError,ValueError):return 'connection or invalid response'
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures={pool.submit(collect,t):t for t in tasks}
            for future in as_completed(futures):
                result=future.result()
                if result=='ok':ok+=1
                elif result=='empty':empty+=1
                else:
                    failed+=1
                    print(f'{futures[future]}: {result}',flush=True)
        # Refresh recent public notices independently; keep old files on failure.
        from datetime import timedelta
        now=datetime.now(ZoneInfo('Asia/Seoul'))
        notice_folder=args.output.parent/'notices'
        notice_folder.mkdir(parents=True,exist_ok=True)
        for stock in wanted:
            corp=lookup[stock]['corp_code']
            try:
                response=client.get('https://opendart.fss.or.kr/api/list.json',params={'crtfc_key':key,'corp_code':corp,'bgn_de':(now-timedelta(days=365)).strftime('%Y%m%d'),'end_de':now.strftime('%Y%m%d'),'page_count':30,'page_no':1,'sort':'date','sort_mth':'desc'})
                response.raise_for_status();payload=response.json()
                if payload.get('status') in ('000','013'):
                    value={'corp_code':corp,'retrieved_at':now.isoformat(timespec='seconds'),'source':'https://opendart.fss.or.kr/api/list.json','rows':payload.get('list',[])}
                    (notice_folder/(corp+'.json')).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')))
            except (httpx.HTTPError,ValueError):print(f'{stock}: notice refresh unavailable; retained previous file')
    coverage={}
    corp_lookup={company['corp_code']:company for company in directory}
    for file in args.output.glob('*.json'):
        try:
            saved=json.loads(file.read_text());corp=saved['corp_code']
            if corp not in corp_lookup:continue
            item=coverage.setdefault(corp,{**corp_lookup[corp],'years':[],'bases':[],'retrieved_at':saved['retrieved_at']})
            if saved['year'] not in item['years']:item['years'].append(saved['year'])
            if saved['basis'] not in item['bases']:item['bases'].append(saved['basis'])
            item['retrieved_at']=max(item['retrieved_at'],saved['retrieved_at'])
        except (OSError,KeyError,ValueError):continue
    for item in coverage.values():item['years'].sort();item['bases'].sort()
    if coverage:
        (args.output.parent/'coverage.json').write_text(json.dumps({'source':'https://opendart.fss.or.kr','companies':list(coverage.values())},ensure_ascii=False,separators=(',',':')))
    print(f'Saved {ok}, no data {empty}, failed {failed}. Existing successful files were retained.')
    return 0 if ok and not failed else 1


if __name__=='__main__':raise SystemExit(main())
