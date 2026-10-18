"""News reading digest from publisher-provided summaries, without paid calls."""
from datetime import datetime,timedelta
from html import escape
import re
from urllib.parse import urlsplit

CATEGORIES={
 '통화정책':('금리','중앙은행','연준','기준금리','통화정책','federal reserve','interest rate','central bank','ecb'),
 '물가·경기':('물가','인플레','고용','성장률','경기','수출','inflation','economy','economic','jobs','gdp','recession'),
 '기업·산업':('기업','반도체','실적','투자','산업','인공지능','삼성','earnings','company','companies','investment','chip','tech','batteries'),
 '금융시장':('증시','주가','환율','채권','유가','금융','증권','stocks','stock market','wall street','bonds','markets','oil','bank'),
}


def published_at(article):
    try:
        value=datetime.fromisoformat(article['published_at'].replace('Z','+00:00'))
        return value if value.tzinfo else None
    except (KeyError,ValueError,TypeError):return None


def relative_time(value,now):
    seconds=max(0,int((now-value).total_seconds()))
    if seconds<60:return '방금'
    if seconds<3600:return f'{seconds//60}분 전'
    if seconds<86400:return f'{seconds//3600}시간 전'
    return f'{seconds//86400}일 전'


def time_markup(article,now):
    at=published_at(article)
    if at is None:return ''
    exact=at.astimezone(now.tzinfo).strftime('%Y.%m.%d %H:%M KST')
    return '<time datetime="'+escape(at.isoformat(),quote=True)+'" title="'+exact+'">'+relative_time(at,now)+'</time>'


def select_digest(articles,now,limit=4):
    eligible=[]
    for article in articles:
        at=published_at(article)
        if at is None or at>now or not article.get('excerpt'):continue
        if urlsplit(article.get('url','')).scheme!='https':continue
        text=(article.get('title','')+' '+article['excerpt']).casefold()
        scores={category:sum(word in text for word in words) for category,words in CATEGORIES.items()}
        category=max(scores,key=scores.get)
        if not scores[category]:continue
        eligible.append((article,category,scores[category],at))
    recent=[item for item in eligible if item[3]>=now-timedelta(hours=24)]
    pool=recent if len(recent)>=2 else eligible
    pool=sorted(pool,key=lambda item:(item[3]>=now-timedelta(hours=24),item[2],item[3]),reverse=True)
    picked=[];urls=set();sources=set();categories=set()
    for strict in (True,False):
        for article,category,score,at in pool:
            if article['url'] in urls:continue
            if strict and (category in categories or article['source'] in sources):continue
            picked.append({**article,'category':category})
            urls.add(article['url']);sources.add(article['source']);categories.add(category)
            if len(picked)==limit:return picked
    return picked


def summary_text(article):
    text=re.sub(r'\s+',' ',article.get('excerpt','')).strip()
    sentences=re.split(r'(?<=[.!?。])\s+',text)
    summary=' '.join(sentences[:2])
    return summary if len(summary)<=260 else summary[:257].rstrip()+'…'


def render(articles,now):
    import streamlit as st
    items=select_digest(articles,now)
    if not items:return
    html=['<section class="news-digest"><div class="news-digest-head"><h3>주요 뉴스 브리핑</h3><span>기사 요약</span></div><div class="news-digest-grid">']
    for item in items:
        html.append('<article><small>'+escape(item['category'])+'</small><h4><a href="'+escape(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(item['title'])+'</a></h4><p>'+escape(summary_text(item))+'</p><div class="news-digest-meta">'+escape(item['source'])+' · '+time_markup(item,now)+'</div></article>')
    html.append('</div></section>')
    st.markdown(''.join(html),unsafe_allow_html=True)
