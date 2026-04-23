import streamlit as st

st.set_page_config(
    page_title="Tiff 投資研究工具",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Tiff 投資研究工具")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📰 市場資訊日報
    自動彙整 11 個免費來源的最新財經新聞，用 AI 摘要每篇文章的市場影響與基金影響。

    **包含來源：**
    - 路透社、CNBC、MarketWatch、Yahoo Finance
    - 香港金管局（HKMA）、SFC、港交所
    - Morningstar、ETF.com

    👉 點左側「**市場日報**」開始使用
    """)

with col2:
    st.markdown("""
    ### 💼 Portfolio 總覽
    把各平台的持倉 CSV 上傳，自動合併顯示總市值、平台分配、持倉明細。

    **支援平台：**
    - 富途 Futu、Interactive Brokers
    - Binance
    - Syfe、StashAway、Jarsy

    👉 點左側「**Portfolio**」開始使用
    """)

st.markdown("---")
st.caption("所有資料來源均為免費公開資訊。AI 摘要由 Claude Haiku 生成。")
