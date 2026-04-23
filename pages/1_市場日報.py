import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from core.fetch import fetch_all
from core.summarize import summarize, has_ai
from core.config import CATEGORY_LABELS

st.set_page_config(page_title="市場日報", page_icon="📰", layout="wide")
st.title("📰 市場資訊日報")

# ── 側邊欄控制 ──
with st.sidebar:
    st.header("設定")
    hours = st.slider("抓取時間範圍（小時）", 6, 72, 24, step=6)
    ai_enabled = st.toggle("AI 摘要", value=has_ai(),
                           help="需要 Anthropic API Key 或本地 Ollama")
    if not has_ai():
        st.warning("未偵測到 AI 後端。\n\n在 Streamlit Cloud 的 Secrets 加入：\n`ANTHROPIC_API_KEY = \"sk-...\"`")
    refresh = st.button("🔄 重新整理", use_container_width=True)

# ── 快取抓取（1 小時 TTL）──
@st.cache_data(ttl=3600, show_spinner="正在抓取新聞...")
def _fetch(h):
    return fetch_all(max_age_hours=h)

if refresh:
    st.cache_data.clear()

articles = _fetch(hours)

if not articles:
    st.warning("沒有抓到文章，請稍後重試或檢查網路連線。")
    st.stop()

# ── KPI ──
cats = list(CATEGORY_LABELS.keys())
counts = {c: sum(1 for a in articles if a["category"] == c) for c in cats}
cols = st.columns(len(cats) + 1)
cols[0].metric("總文章數", len(articles))
for i, c in enumerate(cats):
    cols[i + 1].metric(CATEGORY_LABELS[c], counts[c])

st.markdown("---")

# ── 分類顯示 ──
tab_labels = [f"{CATEGORY_LABELS[c]} ({counts[c]})" for c in cats if counts[c] > 0]
active_cats = [c for c in cats if counts[c] > 0]
tabs = st.tabs(tab_labels)

for tab, cat in zip(tabs, active_cats):
    with tab:
        cat_articles = [a for a in articles if a["category"] == cat]

        if ai_enabled:
            if st.button(f"⚡ 一鍵摘要全部 {len(cat_articles)} 篇", key=f"batch_{cat}"):
                progress = st.progress(0, text="AI 摘要中...")
                for i, article in enumerate(cat_articles):
                    if not article["summary"]:
                        article["summary"] = summarize(article)
                    progress.progress((i + 1) / len(cat_articles),
                                      text=f"({i+1}/{len(cat_articles)}) {article['title'][:40]}...")
                progress.empty()
                st.rerun()

        for article in cat_articles:
            with st.container():
                col_title, col_time = st.columns([4, 1])
                with col_title:
                    st.markdown(f"**[{article['title']}]({article['link']})**")
                with col_time:
                    st.caption(f"🕐 {article['published'][-12:-4]}")

                st.caption(f"來源：{article['source_name']}")

                if article["summary"]:
                    st.info(article["summary"])
                elif ai_enabled:
                    if st.button("AI 摘要", key=f"sum_{hash(article['title'])}"):
                        with st.spinner("摘要中..."):
                            article["summary"] = summarize(article)
                        st.rerun()
                else:
                    if article.get("content"):
                        with st.expander("原文摘錄"):
                            st.write(article["content"][:500] + "...")

                st.divider()
