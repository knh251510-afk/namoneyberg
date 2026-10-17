"""Small metadata, image category controls and compact report exports."""
from html import escape
import streamlit as st

CATEGORIES={'매크로':'macro','글로벌':'global','산업':'industry'}

def metadata(text):
    st.markdown('<div class="brief-metadata">'+escape(text)+'</div>',unsafe_allow_html=True)

def category_picker():
    selected=st.session_state.get('brief_category','매크로')
    def choose(value):st.session_state['brief_category']=value
    active=CATEGORIES[selected]
    st.markdown(f'<style>.st-key-brief_category_{active} button{{border:2px solid #806751!important;box-shadow:inset 0 -4px 0 #806751!important}}.st-key-brief_category_{active} button p{{color:#614b39!important}}</style>',unsafe_allow_html=True)
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
        a,b,_=st.columns([2,2,5])
        a.download_button('브리핑 다운로드',report_markdown(saved),f'weekly_{start:%Y%m%d}.md','text/markdown')
        b.download_button('마켓 오버뷰 다운로드',json.dumps(saved,ensure_ascii=False,indent=2),'weekly_market_overview.json','application/json')
