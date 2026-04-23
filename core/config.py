SOURCES = [
    {"name": "Reuters Business",    "url": "https://feeds.reuters.com/reuters/businessNews",      "category": "macro"},
    {"name": "Reuters Finance",     "url": "https://feeds.reuters.com/reuters/financialsNews",    "category": "macro"},
    {"name": "CNBC Finance",        "url": "https://feeds.nbcnews.com/cnbc/sections/finance",     "category": "macro"},
    {"name": "MarketWatch",         "url": "https://feeds.marketwatch.com/marketwatch/topstories/","category": "macro"},
    {"name": "Yahoo Finance",       "url": "https://finance.yahoo.com/news/rssindex",             "category": "macro"},
    {"name": "Investing.com",       "url": "https://www.investing.com/rss/news.rss",              "category": "macro"},
    {"name": "HKMA",                "url": "https://www.hkma.gov.hk/eng/rss/latest-press-releases.xml", "category": "regulatory_hk"},
    {"name": "SFC HK",              "url": "https://www.sfc.hk/en/rss/news.xml",                 "category": "regulatory_hk"},
    {"name": "HKEX",                "url": "https://www.hkex.com.hk/eng/newsconsul/hkexnews/listingUpdate/rss.xml", "category": "regulatory_hk"},
    {"name": "ETF.com",             "url": "https://www.etf.com/rss/news",                       "category": "fund"},
    {"name": "Morningstar",         "url": "https://www.morningstar.com/rss/rss.aspx?show=news", "category": "fund"},
]

CATEGORY_LABELS = {
    "macro": "全球宏觀",
    "regulatory_hk": "香港監管機構",
    "fund": "基金 / ETF",
}

MAX_ITEMS_PER_SOURCE = 5

SUMMARY_PROMPT = """你是一位資深投資研究員。請用繁體中文，依格式摘要：

【一句摘要】（≤30字，點出核心事件）
【市場影響】（股市/債市/匯率受影響方向；若無直接影響寫「暫無直接影響」）
【基金影響】（對基金/ETF 的影響，尤其散戶常持有的品種）

新聞標題：{title}
來源：{source}
內容：{content}

影響欄位必須具體，不能只寫「需留意」。"""
