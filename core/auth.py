"""登入：支援 Google OAuth（首選）與 Email 兩種方式"""
import re
import streamlit as st
from core import db

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_oauth_configured() -> bool:
    """檢查 Google OAuth secrets 是否已設定"""
    try:
        auth_cfg = st.secrets.get("auth", {})
        if not auth_cfg:
            return False
        return bool(auth_cfg.get("google") or auth_cfg.get("client_id"))
    except Exception:
        return False


def is_auth_configured() -> bool:
    """有 DB 且（Google OAuth 已設 或 DB 允許 email 登入）"""
    return db.is_configured()


def _logged_in_via_oauth() -> bool:
    try:
        return hasattr(st, "user") and getattr(st.user, "is_logged_in", False)
    except Exception:
        return False


def require_login() -> str | None:
    """
    如果 OAuth 已設定：要求 Google 登入
    否則：要求輸入 email
    若 DB 未設定：直接放行（None）
    """
    if not db.is_configured():
        return None

    oauth_on = _is_oauth_configured()

    # ── Google OAuth 模式 ──
    if oauth_on:
        if _logged_in_via_oauth():
            return st.user.email

        st.markdown("### 登入")
        st.caption("用 Google 帳號登入，你的 Portfolio 與 AI 摘要會自動保存。")
        if st.button("使用 Google 登入", type="primary", use_container_width=True):
            st.login("google")
        st.stop()
        return None

    # ── Email fallback 模式 ──
    if st.session_state.get("user_email"):
        return st.session_state.user_email

    st.markdown("### 進入工具")
    st.caption("輸入你常用的 email。你的 Portfolio 與 AI 摘要會用這個 email 自動保存。")
    st.info("💡 Admin 未配置 Google 登入，目前使用 email 模式")

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
    """Sidebar 顯示目前帳號 + 登出按鈕"""
    with st.sidebar:
        if _logged_in_via_oauth():
            st.markdown("---")
            name = getattr(st.user, "name", "") or st.user.email
            st.caption(f"登入：**{name}**")
            if st.button("登出", use_container_width=True):
                st.logout()
        elif st.session_state.get("user_email"):
            st.markdown("---")
            st.caption(f"帳號：**{st.session_state.user_email}**")
            if st.button("切換帳號", use_container_width=True):
                st.session_state.pop("user_email", None)
                st.session_state.pop("summaries", None)
                st.rerun()
