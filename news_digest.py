"""News reading digest from publisher-provided summaries, without paid calls."""
from datetime import datetime,timedelta
from html import escape
import re
from urllib.parse import urlsplit

CATEGORIES={
 '통화정책':('기준금리','정책금리','금리 인하','금리 인상','통화정책','연준','한국은행','federal reserve','interest rate','interest rates','central bank','central banks','fomc','ecb','boj'),
 '물가·경기':('소비자물가','생산자물가','인플레이션','실업률','고용','성장률','경기침체','경기둔화','소매판매','수출','inflation','economy','economic','jobs','gdp','recession'),
 '기업·산업':('반도체','실적','매출','영업이익','투자','자동차','인공지능','삼성','하이닉스','earnings','investment','chip','chips','semiconductor','semiconductors','tech','technology','batteries','ai','nvidia','tesla','microsoft','profits'),
 '금융시장':('증시','주가','환율','국채','채권','유가','금융','증권','코스피','나스닥','stocks','stock market','wall street','bonds','markets','oil','bank of','banking'),
}


def keyword_hits(text,words):
    return sum(bool(re.search(r'\b'+re.escape(word)+r'\b',text)) if word.isascii() else word in text for word in words)



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
        title=article.get('title','').casefold()
        scores={category:keyword_hits(title,words) for category,words in CATEGORIES.items()}
        category=max(scores,key=scores.get)
        if not scores[category]:continue
        score=scores[category]*2+min(1,keyword_hits(article['excerpt'].casefold(),CATEGORIES[category]))
        eligible.append((article,category,score,at))
    pool=sorted(eligible,key=lambda item:item[2]-max(0,(now-item[3]).total_seconds()/3600)/72,reverse=True)
    picked=[];urls=set()
    for category in CATEGORIES:
        for article,kind,score,at in pool:
            if kind==category and article['url'] not in urls:
                picked.append({**article,'category':kind});urls.add(article['url']);break
        if len(picked)==limit:return picked
    for article,category,score,at in pool:
        if article['url'] in urls:continue
        picked.append({**article,'category':category});urls.add(article['url'])
        if len(picked)==limit:break
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
    html=['<section class="news-digest"><div class="news-digest-head"><h3>주요 뉴스 브리핑</h3><span>최근 7일 · 기사 요약</span></div><div class="news-digest-grid">']
    for item in items:
        html.append('<article><small>'+escape(item['category'])+'</small><h4><a href="'+escape(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(item['title'])+'</a></h4><p>'+escape(summary_text(item))+'</p><div class="news-digest-meta">'+escape(item['source'])+' · '+time_markup(item,now)+'</div></article>')
    html.append('</div></section>')
    st.markdown(''.join(html),unsafe_allow_html=True)
