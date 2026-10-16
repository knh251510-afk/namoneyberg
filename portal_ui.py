"""금융 포털형 요약 카드. 실제 수집 데이터만 표시합니다."""
from html import escape
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import macro_data as data


def article_url(theme):
    from urllib.parse import urlsplit
    candidates=[s.get('url','') for s in theme.get('sources',[])]+[theme.get('url','')]
    for url in candidates:
        parsed=urlsplit(url)
        if parsed.scheme in ('https','http') and parsed.netloc:return url
    return ''

def article_link(theme):
    title=escape(theme.get('title',''))
    url=article_url(theme)
    return f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{title} ↗</a>' if url else title


def policy_changes(frame):
    result={}
    if frame.empty:return result
    for country,sub in frame.dropna(subset=['value']).groupby('country'):
        sub=sub.sort_values('date').drop_duplicates('date').copy()
        sub['delta']=sub.value.diff()
        moves=sub[sub.delta.abs()>0.00001]
        if not moves.empty:
            row=moves.iloc[-1]
            result[country]={'change':float(row.delta),'date':pd.Timestamp(row.date).strftime('%Y-%m-%d')}
    return result

def strip(frame,changes=None):
    items=[]
    for _,row in frame.head(5).iterrows():
        v=row.get('정책금리 · %')
        value='—' if pd.isna(v) else f'{v:.2f}%'
        date=str(row.get('정책금리 · % 관측','관측 없음'))
        recent=(changes or {}).get(row.get('country'))
        delta=''
        if recent:
            change=recent['change']
            cls='rise' if change>0 else 'fall'
            text=f'▲ +{change:.2f}' if change>0 else f'▼ {change:.2f}'
            delta=f'<small class="rate-change {cls}">{text} %p <span>최근 변경 · {recent["date"]}</span></small>'
        else:
            delta='<small class="rate-change flat">변경 이력 확인 불가</small>'
        items.append(f'<div class="ticker-item"><span>{escape(row["경제권"])} 정책금리</span><strong>{value}</strong>{delta}<small>자료 기준 {escape(date)}</small></div>')
    st.markdown('<div class="market-strip">'+''.join(items)+'</div>',unsafe_allow_html=True)


def cards(themes):
    ordered=[]
    for category in ('매크로','글로벌','산업'):
        match=next((t for t in themes if t.get('category')==category),None)
        if match:ordered.append(match)
    ordered.extend(t for t in themes if t not in ordered)
    blocks=[]
    for i,t in enumerate(ordered[:3]):
        category=t.get('category','리서치')
        title=t.get('title','')
        text=t.get('facts',t.get('excerpt',''))
        text=text[:140]+('…' if len(text)>140 else '')
        href=article_url(t) or '/news'
        if not href.startswith(('https://','/')):href='/weekly'
        asset={'매크로':'macro','글로벌':'global','산업':'industry'}.get(category,'global')
        blocks.append(f'<a class="research-card tone-{i}" href="{escape(href,quote=True)}" target="_blank" rel="noopener noreferrer"><img class="brief-image" src="/app/static/brief-{asset}.png" alt="{escape(category)} 주제 AI 일러스트" loading="lazy"><span class="card-category">{escape(category)}</span><h3>{escape(title)}</h3><p>{escape(text)}</p><span class="card-more">자세히 보기 <span aria-hidden="true">↗</span></span></a>')
    st.markdown('<div class="research-grid">'+''.join(blocks)+'</div>',unsafe_allow_html=True)


def home_brief():
    start,_=data.week_bounds()
    saved=st.session_state.get('weekly_report')
    if not saved:
        folder=Path(__file__).resolve().parent/'macro_reports'
        for path in sorted(folder.glob('overview_*.json'),reverse=True):
            try:
                candidate=json.loads(path.read_text())
                if candidate.get('period',{}).get('start')==start.isoformat():saved=candidate;break
            except (ValueError,OSError):continue
    st.markdown('<div class="section-heading"><div><span class="section-kicker">WEEKLY INSIGHT</span><h2>이번 주 글로벌 브리프</h2></div><a href="#weekly-review">시장 해설 ↓</a></div>',unsafe_allow_html=True)
    if saved and saved.get('period',{}).get('start')==start.isoformat():
        cards([{**t,'url':'/weekly'} for t in saved['report']['themes']])
    else:
        articles,status=data.news()
        ranked=data.prioritize_news(articles)
        themes=[]
        rules=[('매크로',['금리','물가','inflation','rate','국채','고용','경제','economy']),
               ('글로벌',['중국','미국','일본','china','trade','tariff','global','world','무역']),
               ('산업',['반도체','ai','chip','oil','energy','에너지','원유','자동차','산업'])]
        used=set()
        for category,keywords in rules:
            item=next((a for a in ranked if a['url'] not in used and any(k in a['title'].lower() for k in keywords)),None)
            if item:
                themes.append({**item,'category':category});used.add(item['url'])
        if themes:
            cards(themes)
            with st.expander('브리프 출처 · 수집 범위',expanded=False):
                for t in themes:st.caption(f"[{t['source']} · {t['published_at'][:10]}]({t['url']})")
                st.caption('기사 제목과 RSS 제공 설명을 사용합니다. AI 종합 리포트가 아닙니다.')
        else:st.info('수집된 이번 주 뉴스가 없습니다. 마켓 오버뷰에서 새로고침해주세요.')
