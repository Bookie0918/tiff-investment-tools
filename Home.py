import streamlit as st
from core.style import inject
from core.auth import require_login, sidebar_user_panel, is_auth_configured
from core import db

st.set_page_config(
    page_title="Tiff 投資研究工具",
    page_icon="📊",
    layout="wide",
)
inject()

st.title("Tiff 投資研究工具")
st.caption("Market intelligence · Portfolio overview")

# ── 登入（如果已配置 OAuth）──
if is_auth_configured():
    email = require_login()
    sidebar_user_panel()
else:
    email = None
    st.info("提示：資料庫未設定，目前網站可使用但上傳的資料不會保存。")

st.markdown("---")

# ── 帳號狀態區 ──
if email:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(f"### 歡迎，{email}")
        try:
            last = db.last_upload_time(email) if db.is_configured() else None
            if last:
                st.caption(f"上次更新 Portfolio：{last.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.caption("尚未上傳過 Portfolio")
        except Exception as e:
            st.caption("首次使用")
            with st.expander("⚠ 資料庫連線有問題", expanded=False):
                st.code(f"{type(e).__name__}: {str(e)[:500]}")
                st.info("可能原因：\n1. Supabase 的 `holdings` 和 `summaries` 表還沒建立（需要在 SQL Editor 跑 schema）\n2. SUPABASE_KEY 填錯（要 anon public key）")
    with col_b:
        st.success("資料已連線，自動保存")
    st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 市場資訊日報")
    st.markdown("""
自動彙整 11 個免費財經來源，用 AI 摘要每篇文章的**市場影響**與**基金影響**。

**來源包含：**
- 路透、CNBC、MarketWatch、Yahoo Finance
- 香港金管局、SFC、港交所
- Morningstar、ETF.com

左側選「**市場日報**」開始。
""")

with col2:
    st.markdown("### Portfolio 總覽")
    st.markdown("""
上傳各平台的持倉 CSV，自動合併顯示**總市值**、**平台分配**、**持倉明細**。

**支援平台：**
- 富途 Futu、Interactive Brokers
- Binance
- Syfe、StashAway、Jarsy

左側選「**Portfolio**」開始。
""")

st.markdown("---")
st.caption("所有資料來源均為免費公開資訊 · AI 摘要由 Claude Haiku 生成")
