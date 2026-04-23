"""簡易 Email 登入：輸入 email → 用 email 當帳號 key 存 Supabase"""
import re
import streamlit as st
from core import db

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_auth_configured() -> bool:
    """有 DB 才需要登入"""
    return db.is_configured()


def require_login() -> str | None:
    """若 DB 已設定，必須輸入 email；否則直接放行"""
    if not db.is_configured():
        return None

    if st.session_state.get("user_email"):
        return st.session_state.user_email

    st.markdown("### 進入工具")
    st.caption("輸入你常用的 email。你的 Portfolio 和 AI 摘要會用這個 email 自動保存，下次輸入同一個 email 即可載回。")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@gmail.com")
        submitted = st.form_submit_button("進入", type="primary", use_container_width=True)
        if submitted:
            cleaned = (email or "").strip().lower()
            if EMAIL_PATTERN.match(cleaned):
                st.session_state.user_email = cleaned
                st.rerun()
            else:
                st.error("請輸入有效的 email（例如 tiff@gmail.com）")

    st.stop()
    return None


def sidebar_user_panel():
    """sidebar 顯示目前帳號 + 切換按鈕"""
    if st.session_state.get("user_email"):
        with st.sidebar:
            st.markdown("---")
            st.caption(f"帳號：**{st.session_state.user_email}**")
            if st.button("切換帳號", use_container_width=True):
                st.session_state.pop("user_email", None)
                st.session_state.pop("summaries", None)
                st.rerun()
