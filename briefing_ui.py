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

def category_picker():
    selected=st.session_state.get('brief_category','매크로')
    def choose(value):st.session_state['brief_category']=value
    active=CATEGORIES[selected]
    st.markdown(f'<style>.st-key-brief_category_{active} button{{border:2px solid var(--seed-color-bg-brand-solid)!important;box-shadow:inset 0 -4px 0 var(--seed-color-bg-brand-solid)!important}}.st-key-brief_category_{active} button p{{color:#fff!important}}</style>',unsafe_allow_html=True)
    rules=[]
    for asset in CATEGORIES.values():
        from ui_theme import mode
        uri=category_image(asset,mode())
        rules.append(f'.st-key-brief_category_{asset} button,.st-key-brief_category_{asset} button:hover'+ '{background-image:url("'+uri+'")!important;}')
    st.markdown('<style>'+''.join(rules)+'</style>',unsafe_allow_html=True)
    cols=st.columns(3)
    for col,(label,asset) in zip(cols,CATEGORIES.items()):
        with col:
            with st.container(key='brief_category_'+asset):
                st.button(label,key='choose_brief_'+asset,on_click=choose,args=(label,),width='stretch')
    return selected

def downloads(saved,start):
    import json
    from macro_ai import report_markdown
    with st.container(key='brief_downloads'):
        a,b=st.columns(2,gap='small')
        a.download_button('브리핑 문서 (.md)',report_markdown(saved),f'weekly_{start:%Y%m%d}.md','text/markdown')
        b.download_button('데이터 (.json)',json.dumps(__import__('briefing_store').public_report(saved),ensure_ascii=False,indent=2),'weekly_market_overview.json','application/json')

@st.fragment
def topics(report):
    category=category_picker()
    themes=[t for t in report.get('themes',[]) if t.get('category')==category]
    if not themes:
        st.info('이 범주의 근거가 충분한 뉴스가 없습니다.')
        return
    blocks=[]
    for theme in themes:
        sources=''.join('<a href="'+escape(item['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(item['source']+' · '+item['title'])+' ↗</a>' for item in theme.get('sources',[]))
        comparison=('<dt>보도 비교</dt><dd>'+escape(theme['comparison'])+'</dd>') if theme.get('comparison') else ''
        blocks.append('<article class="brief-topic"><h4>'+escape(theme.get('title',''))+'</h4><dl><dt>종합 흐름</dt><dd>'+escape(theme.get('facts',''))+'</dd><dt>시장 의미</dt><dd>'+escape(theme.get('interpretation',''))+'</dd><dt>확인할 변수</dt><dd>'+escape(theme.get('watch',''))+'</dd>'+comparison+'</dl><details class="brief-sources"><summary>출처 '+str(len(theme.get('sources',[])))+'건</summary>'+sources+'</details></article>')
    st.markdown('<div class="brief-topics">'+''.join(blocks)+'</div>',unsafe_allow_html=True)
