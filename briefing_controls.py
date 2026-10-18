"""Public generation control; authorization is checked before any service call."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import admin_auth


def request_generation(has_articles):
    admin=admin_auth.is_admin()
    if admin:
        st.checkbox('대표 이미지 함께 생성',value=True,key='brief_with_image')
    with st.container(key='brief_generation'):
        clicked=st.button('브리핑 생성 · 최신화',icon=':material/refresh:',disabled=admin and not has_articles,key='generate_market_brief')
    if not clicked:return False
    if not admin_auth.is_admin():
        st.toast('관리자만 사용할 수 있습니다.',icon='🔒')
        st.warning('브리핑 생성과 최신화는 관리자만 사용할 수 있습니다.')
        return False
    return bool(has_articles)


def updated_label(saved):
    raw=(saved or {}).get('generated_at')
    try:
        at=datetime.fromisoformat(raw)
        if at.tzinfo is None:return '최신화 시각 확인 불가'
        return '최신화 '+at.astimezone(ZoneInfo('Asia/Seoul')).strftime('%Y.%m.%d %H:%M')+' KST'
    except (TypeError,ValueError):return '아직 생성된 브리핑이 없습니다.' if not saved else '최신화 시각 확인 불가'
