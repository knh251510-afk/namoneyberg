"""Small metadata, image category controls and compact report exports."""
from html import escape
import streamlit as st
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

CATEGORIES={'매크로':'macro','글로벌':'global','산업':'industry'}

def metadata(text):
    st.markdown('<div class="brief-metadata">'+escape(text)+'</div>',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def category_image(asset,mode='light'):
    from theme_assets import image_path
    source=image_path('brief-'+asset,mode)
    image=Image.open(source).convert('RGB')
    image.thumbnail((640,400))
    out=BytesIO();image.save(out,format='JPEG',quality=72,optimize=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(out.getvalue()).decode()


def lead(saved):
    report=saved.get('report',{})
    art=saved.get('cover_image') or {}
    image=''
    if art.get('mime') in ('image/jpeg','image/png','image/webp') and art.get('b64'):
        try:
            base64.b64decode(art['b64'],validate=True)
            image='<img class="overview-cover" alt="'+escape(art.get('alt','브리핑 대표 이미지'),quote=True)+'" src="data:'+art['mime']+';base64,'+art['b64']+'">'
        except ValueError:pass
    layout=' has-cover' if image else ''
    st.markdown('<section class="overview-lead'+layout+'"><div><h2>'+escape(report.get('headline',''))+'</h2><p>'+escape(report.get('summary',''))+'</p></div>'+image+'</section>',unsafe_allow_html=True)

def downloads(saved,start):
    import json
    from macro_ai import report_markdown
    with st.container(key='brief_downloads'):
        a,b=st.columns(2,gap='small')
        a.download_button('브리핑 문서 (.md)',report_markdown(saved),f'weekly_{start:%Y%m%d}.md','text/markdown')
        b.download_button('데이터 (.json)',json.dumps(__import__('briefing_store').public_report(saved),ensure_ascii=False,indent=2),'weekly_market_overview.json','application/json')

def render_category(report,category):
    themes=[t for t in report.get('themes',[]) if t.get('category')==category]
    if not themes:
        st.caption('이 범주에 게시된 주제가 없습니다.')
        return
    blocks=[]
    for theme in themes:
        sources=''.join('<a href="'+escape(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(item['source']+' · '+item['title'])+' ↗</a>' for item in theme.get('sources',[]))
        comparison=('<dt>보도 비교</dt><dd>'+escape(theme['comparison'])+'</dd>') if theme.get('comparison') else ''
        blocks.append('<article class="brief-topic"><h4>'+escape(theme.get('title',''))+'</h4><dl><dt>종합 흐름</dt><dd>'+escape(theme.get('facts',''))+'</dd><dt>시장 의미</dt><dd>'+escape(theme.get('interpretation',''))+'</dd><dt>확인할 변수</dt><dd>'+escape(theme.get('watch',''))+'</dd>'+comparison+'</dl><details class="brief-sources"><summary>출처 '+str(len(theme.get('sources',[])))+'건</summary>'+sources+'</details></article>')
    st.markdown('<div class="brief-topics">'+''.join(blocks)+'</div>',unsafe_allow_html=True)


def topics(report):
    from ui_theme import mode
    rules=[]
    for index,asset in enumerate(CATEGORIES.values(),1):
        uri=category_image(asset,mode())
        rules.append('.st-key-overview_categories [role="tab"]:nth-of-type('+str(index)+')::before{background-image:url("'+uri+'")!important;}')
    st.markdown('<style>'+''.join(rules)+'</style>',unsafe_allow_html=True)
    with st.container(key='overview_categories'):
        tabs=st.tabs(list(CATEGORIES))
        for (category,_),tab in zip(CATEGORIES.items(),tabs):
            with tab:
                render_category(report,category)
