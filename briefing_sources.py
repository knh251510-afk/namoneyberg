"""Explicit source categories and verbatim numeric candidates for the evidence stage."""
import re
from urllib.parse import urlsplit
OFFICIAL={'federalreserve.gov','bls.gov','bea.gov','ecb.europa.eu','bok.or.kr','kostat.go.kr','kosis.kr','imf.org','worldbank.org','bis.org','opendart.fss.or.kr'}
WIRES={'reuters.com','apnews.com','yna.co.kr','yonhapnews.co.kr'}
def enrich(row):
    host=(urlsplit(row.get('url','')).hostname or '').lower()
    match=lambda domains:any(host==domain or host.endswith('.'+domain) for domain in domains)
    grade='공식' if match(OFFICIAL) else '통신사' if match(WIRES) else '매체'
    raw=row.get('title','')+' '+row.get('excerpt','')
    return {**row,'source_grade':grade,'numeric_candidates':re.findall(r'[-+]?\d[\d,]*(?:\.\d+)?\s*(?:%p|%|bp|조|억|만)?',raw),'evidence_scope':'제목과 제공 요약'}
