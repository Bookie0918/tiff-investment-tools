"""Google OAuth 登入包裝（Streamlit 1.42+ native auth）"""
import streamlit as st


def require_login() -> str | None:
    """
    如果使用者未登入，顯示登入按鈕，回傳 None 並 st.stop()。
    如果已登入，回傳 email。
    """
    # Streamlit 1.42+ 的 st.user API
    if not hasattr(st, "user") or not getattr(st.user, "is_logged_in", False):
        st.markdown("### 登入")
        st.caption("用 Google 帳號登入後，你的 portfolio 和 AI 摘要會自動保存，下次登入直接載入。")
        if st.button("使用 Google 登入", type="primary"):
            st.login("google")
        st.stop()
        return None
    return st.user.email


def sidebar_user_panel():
    """在 sidebar 顯示登入狀態 + 登出按鈕"""
    if hasattr(st, "user") and getattr(st.user, "is_logged_in", False):
        with st.sidebar:
            st.markdown("---")
            name = getattr(st.user, "name", "") or st.user.email
            st.caption(f"已登入：**{name}**")
            if st.button("登出", use_container_width=True):
                st.logout()


def is_auth_configured() -> bool:
    """檢查 OAuth secrets 是否已配置"""
    try:
        return bool(st.secrets.get("auth", {}).get("google"))
    except Exception:
        return False
