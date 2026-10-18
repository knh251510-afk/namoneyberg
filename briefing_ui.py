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
def category_image(asset):
    source=Path(__file__).parent/'static'/f'brief-{asset}.png'
    image=Image.open(source).convert('RGB')
    image.thumbnail((640,400))
    out=BytesIO();image.save(out,format='JPEG',quality=72,optimize=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(out.getvalue()).decode()

def category_picker():
    selected=st.session_state.get('brief_category','매크로')
    def choose(value):st.session_state['brief_category']=value
    active=CATEGORIES[selected]
    st.markdown(f'<style>.st-key-brief_category_{active} button{{border:2px solid var(--seed-color-bg-brand-solid)!important;box-shadow:inset 0 -4px 0 var(--seed-color-bg-brand-solid)!important}}.st-key-brief_category_{active} button p{{color:var(--seed-color-palette-carrot-800)!important}}</style>',unsafe_allow_html=True)
    rules=[]
    for asset in CATEGORIES.values():
        uri=category_image(asset)
        rules.append(f'.st-key-brief_category_{asset} button,.st-key-brief_category_{asset} button:hover'+ '{background-image:url("'+uri+'")!important;}')
    st.markdown('<style>'+''.join(rules)+'</style>',unsafe_allow_html=True)
    cols=st.columns(3)
    for col,(label,asset) in zip(cols,CATEGORIES.items()):
        with col:
            with st.container(key='brief_category_'+asset):
                st.button(label,key='choose_brief_'+asset,on_click=choose,args=(label,),use_container_width=True)
    return selected

def downloads(saved,start):
    import json
    from macro_ai import report_markdown
    with st.container(key='brief_downloads'):
        a,b=st.columns(2,gap='small')
        a.download_button('브리핑 다운로드',report_markdown(saved),f'weekly_{start:%Y%m%d}.md','text/markdown')
        b.download_button('마켓 오버뷰 다운로드',json.dumps(saved,ensure_ascii=False,indent=2),'weekly_market_overview.json','application/json')
