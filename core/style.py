"""withbookie.com 米白書感主題 — 套用到每個 Streamlit 頁面"""
import streamlit as st

_CUSTOM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">

<style>
:root {
    --bg: #f4efe6;
    --card: #ebe5da;
    --border: #d5cfc4;
    --border2: #ddd8cc;
    --text: #1c1810;
    --muted: #7a7060;
    --muted2: #968e7e;
    --accent: #8a6a10;
    --font: 'DM Sans', 'Noto Sans TC', sans-serif;
    --serif: 'Instrument Serif', Georgia, serif;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stMarkdown p,
div[data-testid="stMarkdownContainer"], div[data-testid="stText"] {
    font-family: var(--font) !important;
    color: var(--text);
}

/* 主背景 */
.stApp { background: var(--bg) !important; }

/* 標題全部用 serif italic */
h1, h2, h3, h4 {
    font-family: var(--serif) !important;
    font-style: italic;
    color: var(--accent) !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em;
}
h1 { font-size: clamp(28px, 5vw, 40px) !important; }
h2 { font-size: clamp(22px, 3.5vw, 28px) !important; }
h3 { font-size: clamp(18px, 2.5vw, 22px) !important; }

/* 側邊欄 */
section[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text); }

/* 按鈕 — 書頁風格（邊框 + 透明底） */
.stButton > button, .stDownloadButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 2px !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 16px 20px;
}
div[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: var(--serif) !important;
    font-style: italic;
    font-weight: 400 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: var(--muted) !important;
    font-family: var(--font) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    font-weight: 700 !important;
}
div[data-baseweb="tab-highlight"] { background: var(--accent) !important; }

/* Info box (摘要顯示) */
div[data-testid="stAlert"] {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-left: 3px solid var(--accent) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
}
div[data-testid="stAlert"] * { color: var(--text) !important; }

/* Divider */
hr { border-color: var(--border) !important; opacity: 0.6; }

/* 連結 */
a { color: var(--accent) !important; text-decoration: none; }
a:hover { text-decoration: underline; }

/* 表格 */
.stDataFrame, .stTable {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 2px;
}

/* File uploader */
section[data-testid="stFileUploaderDropzone"] {
    background: var(--card) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 2px !important;
}

/* Progress bar */
div[data-testid="stProgress"] > div > div {
    background: var(--accent) !important;
}

/* 隱藏 Streamlit 的 "Made with Streamlit" 頁腳 */
footer, [data-testid="stDecoration"] { display: none; }

/* Container spacing */
.block-container {
    padding-top: 3rem !important;
    max-width: 960px !important;
}

/* Caption（小字說明） */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--muted2) !important;
    font-size: 12px !important;
    letter-spacing: 0.3px;
}
</style>
"""

def inject():
    """在每個頁面最開頭呼叫一次"""
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)
