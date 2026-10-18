"""Five navigation groups with native Streamlit session-preserving links."""
import streamlit as st

GROUPS=[('브리핑',['overview','news']),('데이터',['indicators','statistics','quotes','compare']),('기업 분석',['corporate']),('발표 일정',['calendar']),('개념 지도',['glossary'])]

def render(pages,active):
    by_path={p.url_path:p for p in pages}
    for title,paths in GROUPS:
        members=[by_path[path] for path in paths if path in by_path]
        if not members:continue
        selected=active.url_path in paths
        with st.container(key='nav_group_'+paths[0]):
            if selected:
                scope='.st-key-main_navigation .st-key-nav_group_'+paths[0]
                st.markdown('<style>'+scope+' a,'+scope+' button{background:var(--nb-soft)!important;color:var(--nb-accent)!important;box-shadow:none!important}'+scope+' a:hover,'+scope+' button:hover{background:var(--nb-hover)!important;color:var(--nb-accent)!important}</style>',unsafe_allow_html=True)
            if len(members)>1:
                with st.popover(title,use_container_width=False):
                    for page in members:st.page_link(page,label=page.title)
            else:st.page_link(members[0],label=title)
