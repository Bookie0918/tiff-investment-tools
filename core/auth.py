"""登入：純 email 模式"""
import re
import streamlit as st
from core import db

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_auth_configured() -> bool:
    """有 DB 就啟用 email 登入"""
    return db.is_configured()


def require_login() -> str | None:
    """要求輸入 email。若 DB 未設定：直接放行（None）"""
    if not db.is_configured():
        return None

    if st.session_state.get("user_email"):
        return st.session_state.user_email

    st.markdown("### 進入工具")
    st.caption("輸入你常用的 email。你的 Portfolio 與 AI 摘要會用這個 email 自動保存。")

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
    """Sidebar 顯示目前帳號 + 切換按鈕"""
    with st.sidebar:
        if st.session_state.get("user_email"):
            st.markdown("---")
            st.caption(f"帳號：**{st.session_state.user_email}**")
            if st.button("切換帳號", use_container_width=True):
                st.session_state.pop("user_email", None)
                st.session_state.pop("summaries", None)
                st.rerun()
