import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from core.fetch import fetch_all
from core.summarize import summarize, has_ai
from core.config import CATEGORY_LABELS
from core.style import inject
from core.auth import require_login, sidebar_user_panel, is_auth_configured
from core import db

st.set_page_config(page_title="市場日報", page_icon="📰", layout="wide")
inject()
st.title("市場資訊日報")

# ── 登入 ──
if is_auth_configured():
    email = require_login()
    sidebar_user_panel()
else:
    email = None

# ── 初始化：從 DB 載入上次摘要 ──
if "summaries" not in st.session_state:
    st.session_state.summaries = {}
    if email and db.is_configured():
        st.session_state.summaries = db.load_summaries(email)

# ── 側邊欄 ──
with st.sidebar:
    st.markdown("### 設定")
    hours = st.slider("抓取時間範圍（小時）", 6, 72, 24, step=6)
    ai_available = has_ai()
    ai_enabled = st.toggle("AI 摘要", value=ai_available, disabled=not ai_available,
                           help="需要 Gemini API Key")
    if not ai_available:
        st.warning("未偵測到 AI 後端。\n\n請在 Streamlit Cloud → Settings → Secrets 加入：\n`GEMINI_API_KEY = \"AIza...\"`\n\n免費申請：aistudio.google.com")
    st.markdown("---")
    refresh = st.button("重新整理", use_container_width=True)
    if st.session_state.summaries:
        if st.button(f"清除 {len(st.session_state.summaries)} 筆摘要", use_container_width=True):
            st.session_state.summaries = {}
            if email and db.is_configured():
                db.clear_summaries(email)
            st.rerun()

# ── 抓取新聞 ──
@st.cache_data(ttl=3600, show_spinner="正在抓取新聞...")
def _fetch(h):
    return fetch_all(max_age_hours=h)

if refresh:
    st.cache_data.clear()

articles = _fetch(hours)
if not articles:
    st.warning("沒有抓到文章，請稍後重試。")
    st.stop()

# ── KPI ──
cats = list(CATEGORY_LABELS.keys())
counts = {c: sum(1 for a in articles if a["category"] == c) for c in cats}
cols = st.columns(len(cats) + 1)
cols[0].metric("總文章數", len(articles))
for i, c in enumerate(cats):
    cols[i + 1].metric(CATEGORY_LABELS[c], counts[c])

st.markdown("---")

def _get_summary(article):
    return st.session_state.summaries.get(article["link"])

def _is_error(text: str) -> bool:
    return text.startswith("[") and ("錯誤" in text or "失敗" in text or "error" in text.lower())

def _save_summary(article, summary_text):
    st.session_state.summaries[article["link"]] = summary_text
    # 失敗的不存 DB，讓下次可以重試
    if email and db.is_configured() and not _is_error(summary_text):
        try:
            db.save_summary(email, article["link"], article["title"], summary_text)
        except Exception:
            pass

# ── 分類顯示 ──
tab_labels = [f"{CATEGORY_LABELS[c]} ({counts[c]})" for c in cats if counts[c] > 0]
active_cats = [c for c in cats if counts[c] > 0]
tabs = st.tabs(tab_labels)

for tab, cat in zip(tabs, active_cats):
    with tab:
        cat_articles = [a for a in articles if a["category"] == cat]

        if ai_enabled:
            # 把錯誤訊息當作未摘要，允許重試
            unsummarized = [a for a in cat_articles if not _get_summary(a) or _is_error(_get_summary(a))]
            if unsummarized:
                if st.button(f"一鍵摘要本類 {len(unsummarized)} 篇",
                             key=f"batch_{cat}", use_container_width=True):
                    progress = st.progress(0, text="AI 摘要中（每篇間隔 5 秒避免超過 API 速率限制）...")
                    for i, article in enumerate(unsummarized):
                        if i > 0:
                            time.sleep(5)  # 避免超過 Gemini 15 RPM
                        try:
                            summary_text = summarize(article)
                            _save_summary(article, summary_text)
                        except Exception as e:
                            _save_summary(article, f"[摘要失敗: {e}]")
                        progress.progress(
                            (i + 1) / len(unsummarized),
                            text=f"({i+1}/{len(unsummarized)}) {article['title'][:40]}..."
                        )
                    progress.empty()
                    st.rerun()
            else:
                st.success("本類全部已摘要")

        st.markdown("")

        for article in cat_articles:
            col_title, col_time = st.columns([5, 1])
            with col_title:
                st.markdown(f"**[{article['title']}]({article['link']})**")
            with col_time:
                st.caption(article['published'][-12:-4])

            st.caption(f"{article['source_name']}")

            existing = _get_summary(article)
            if existing:
                st.info(existing)
            elif ai_enabled:
                if st.button("AI 摘要", key=f"sum_{hash(article['link'])}"):
                    with st.spinner("摘要中..."):
                        try:
                            summary_text = summarize(article)
                            _save_summary(article, summary_text)
                        except Exception as e:
                            _save_summary(article, f"[摘要失敗: {e}]")
                    st.rerun()
            else:
                if article.get("content"):
                    with st.expander("原文摘錄"):
                        st.write(article["content"][:500] + "...")

            st.divider()
