"""Explicit admin approval: generation never publishes automatically."""
from copy import deepcopy
import streamlit as st
import admin_auth
import briefing_store

def render():
    if not admin_auth.is_admin():return
    draft=st.session_state.get('briefing_draft')
    if not draft:return
    with st.expander('브리핑 초안 검토 · 게시',expanded=True):
        from briefing_art import render as render_art
        render_art(draft,key='brief_cover_draft')
        edited=deepcopy(draft)
        draft_id=draft['generated_at']
        with st.form('briefing_editor_'+draft_id):
            r=edited['report']
            r['headline']=st.text_input('제목',r['headline'])
            r['summary']=st.text_area('종합 해설',r['summary'],height=150)
            for i,t in enumerate(r['themes']):
                st.markdown('**'+t['category']+' · 주제 '+str(i+1)+'**')
                t['title']=st.text_input('주제 제목',t['title'],key=f'edit_title_{draft_id}_{i}')
                for field,label in [('facts','관측 사실'),('interpretation','전달 경로 · 시장 의미'),('watch','바뀔 조건 · 확인할 변수')]:
                    t[field]=st.text_area(label,t[field],key=f'edit_{field}_{draft_id}_{i}',height=100)
            approved=st.form_submit_button('검토 완료 · 게시',type='primary')
        if approved:
            try:
                edited.pop('validation',None)
                edited.pop('editorial_review',None)
                edited['editorial_changes']={'before':draft['report'],'after':edited['report']}
                edited['publication_status']='approved'
                briefing_store.publish(edited)
                st.session_state.pop('briefing_draft',None)
                st.success('검토한 브리핑을 저장소에 게시했습니다.');st.rerun()
            except (ValueError,PermissionError) as exc:st.error(str(exc))
