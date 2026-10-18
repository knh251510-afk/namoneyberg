"""Date-matched official policy release excerpts, without generation calls."""
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
import json,re
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import macro_data as data

FEEDS={
 '미국':'https://www.federalreserve.gov/feeds/press_monetary.xml',
 '유로존':'https://www.ecb.europa.eu/rss/press.html',
 '영국':'https://www.bankofengland.co.uk/rss/news',
 '일본':'https://www.boj.or.jp/en/rss/whatsnew.xml',
 '한국':'https://www.bok.or.kr/portal/bbs/P0000559/news.rss?menuNo=200690',
}
POLICY=('fomc statement','monetary policy decisions','bank rate','monetary policy summary','statement on monetary policy','통화정책방향','기준금리','금융통화위원회 의사록')

def is_policy(title):return any(x in title.casefold() for x in ('통화정책','금융정책','금융통화위원회','fomc'))

def parse_feed(raw,country):
    root=ET.fromstring(raw);out=[]
    for item in root.iter():
        if item.tag.split('}')[-1] not in ('item','entry'):continue
        fields={c.tag.split('}')[-1]:c for c in item}
        def text(*names):
            for name in names:
                node=fields.get(name)
                if node is not None:return ''.join(node.itertext()).strip()
            return ''
        title=unescape(text('title'))
        if not any(word in title.casefold() for word in POLICY):continue
        url=text('link')
        if not url and fields.get('link') is not None:url=fields['link'].get('href','')
        host=urlparse(url).hostname or ''
        expected=urlparse(FEEDS[country]).hostname
        if urlparse(url).scheme!='https' or host!=expected:continue
        stamp=text('pubDate','date','published','updated')
        try:
            try:dt=pd.Timestamp(parsedate_to_datetime(stamp))
            except (ValueError,TypeError):dt=pd.Timestamp(stamp)
            if dt.tzinfo is None:dt=dt.tz_localize(data.KST)
            day=dt.tz_convert(data.KST).strftime('%Y-%m-%d')
        except (ValueError,TypeError):continue
        summary=BeautifulSoup(unescape(text('description','summary','encoded')),'html.parser').get_text(' ',strip=True)
        # Keep the institution's own excerpt, at most 100 words.
        summary=' '.join(summary.split()[:100])[:650]
        out.append({'country':country,'day':day,'title':title,'summary':summary,'url':url})
    return out

@st.cache_data(ttl=3600,show_spinner=False)
def feed(country):
    raw,_=data.fetch(FEEDS[country],3600)
    rows=parse_feed(raw,country)
    for row in rows[:8]:
        if row['summary'] and row['summary']!=row['title']:continue
        try:
            body,_=data.fetch(row['url'],3600)
            soup=BeautifulSoup(body,'html.parser')
            candidates=[p.get_text(' ',strip=True) for p in soup.select('main p,article p,#content p')]
            selected=[t for t in candidates if re.search(r'\b(decided|voted|maintain|raised?|reduced?)\b|기준금리|운용하기로',t,re.I)]
            row['summary']=' '.join(' '.join(selected[:2]).split()[:100])[:650]
        except Exception:pass
    return rows

def saved_results():
    try:return json.loads(Path(__file__).with_name('calendar_policy_results.json').read_text())['rows']
    except (OSError,ValueError,KeyError):return []

def collect(frame,current):
    countries={r['country'] for _,r in frame.iterrows() if r['when']<current and is_policy(r['title'])}
    rows=saved_results()
    def one(country):
        try:return feed(country)
        except Exception:return []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for more in pool.map(one,countries):rows.extend(more)
    return rows

def result(row,rows):
    day=row['when'].strftime('%Y-%m-%d')
    matches=[r for r in rows if r['country']==row['country'] and r['day']==day]
    matches.sort(key=lambda r:('의사록' in r['title'],not bool(r['summary'])))
    return matches[0] if matches else None
