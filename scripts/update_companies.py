"""Refresh public company names/codes from KRX KIND; run manually before release."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json,re
import httpx
from bs4 import BeautifulSoup
URL='https://kind.krx.co.kr/corpgeneral/corpList.do'
def main():
    response=httpx.get(URL,params={'method':'download','searchType':'13'},timeout=30)
    response.raise_for_status();response.encoding='euc-kr'
    companies=[]
    for tr in BeautifulSoup(response.text,'html.parser').select('tr'):
        cells=[td.get_text(strip=True) for td in tr.select('td')]
        if len(cells)>=3 and re.fullmatch('[0-9A-Z]{6}',cells[2]):companies.append({'name':cells[0],'stock_code':cells[2]})
    if len(companies)<2000:raise ValueError('Unexpected company list; preserve existing directory.')
    payload={'source':str(response.url),'retrieved_at':datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat(),'usage_note':'공개 상장법인목록에서 기업명·종목코드만 수록. 재배포 범위 변경 시 KRX 이용약관을 별도 확인.','companies':companies}
    target=Path(__file__).resolve().parents[1]/'static'/'krx-companies.json'
    target.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
if __name__=='__main__':main()
