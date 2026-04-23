import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
from pathlib import Path
from core.importers import auto_detect, FutuImporter, IBImporter, BinanceImporter, GenericImporter

st.set_page_config(page_title="Portfolio 總覽", page_icon="💼", layout="wide")
st.title("💼 Portfolio 總覽")

REQUIRED_COLS = ["symbol", "name", "qty", "market_value", "cost_price",
                 "current_price", "pnl", "currency", "platform"]

PLATFORM_MAP = {
    "futu": ("富途 Futu", FutuImporter),
    "moomoo": ("富途 Futu", FutuImporter),
    "ib": ("Interactive Brokers", IBImporter),
    "interactive": ("Interactive Brokers", IBImporter),
    "binance": ("Binance", BinanceImporter),
    "syfe": ("Syfe", GenericImporter),
    "stashaway": ("StashAway", GenericImporter),
    "stash": ("StashAway", GenericImporter),
    "jarsy": ("Jarsy", GenericImporter),
}

def detect_platform(filename: str):
    stem = Path(filename).stem.lower()
    for key, (name, cls) in PLATFORM_MAP.items():
        if key in stem:
            return name, cls
    return "其他", GenericImporter

def load_csv(uploaded_file) -> pd.DataFrame | None:
    platform_name, importer_cls = detect_platform(uploaded_file.name)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        if importer_cls in (GenericImporter,):
            importer = importer_cls(tmp_path, platform_name=platform_name)
        else:
            importer = importer_cls(tmp_path)
        df = importer.load()
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = None
        return df[REQUIRED_COLS], platform_name
    except Exception as e:
        st.error(f"{uploaded_file.name} 解析失敗：{e}")
        return None, platform_name
    finally:
        os.unlink(tmp_path)

# ── 上傳區 ──
st.markdown("### 上傳持倉 CSV")
st.caption("命名包含平台名即可自動識別：`futu_xxx.csv`、`binance_xxx.csv`、`ib_xxx.csv`、`syfe_xxx.csv`、`stashaway_xxx.csv`、`jarsy_xxx.csv`")

uploaded_files = st.file_uploader(
    "選擇一個或多個 CSV 檔案",
    type="csv",
    accept_multiple_files=True,
    label_visibility="collapsed",
)

with st.expander("各平台 CSV 匯出方法"):
    st.markdown("""
| 平台 | 匯出路徑 |
|------|---------|
| 富途 Futu | APP → 資產 → 持倉 → 右上角 → 匯出 CSV |
| Interactive Brokers | 帳戶管理 → 報表 → Flex 報表 → Open Positions |
| Binance | 帳戶 → 交易記錄 → 下載 CSV |
| Syfe | 帳戶 → 文件 → Portfolio Statement |
| StashAway | 帳戶 → 對帳單 → 下載 CSV |
| Jarsy | 帳戶設定 → 匯出資料 |
""")

if not uploaded_files:
    st.info("👆 上傳 CSV 後顯示 Portfolio 總覽")
    st.stop()

# ── 載入所有 CSV ──
frames = []
for f in uploaded_files:
    df, platform = load_csv(f)
    if df is not None:
        st.success(f"✅ {f.name} → {platform}（{len(df)} 筆）")
        frames.append(df)

if not frames:
    st.stop()

full_df = pd.concat(frames, ignore_index=True)
full_df["market_value"] = pd.to_numeric(full_df["market_value"], errors="coerce").fillna(0)
full_df["pnl"] = pd.to_numeric(full_df["pnl"], errors="coerce")
total_value = full_df["market_value"].sum()
total_pnl = full_df["pnl"].sum() if full_df["pnl"].notna().any() else None

st.markdown("---")

# ── KPI ──
k1, k2, k3, k4 = st.columns(4)
k1.metric("總市值", f"{total_value:,.0f}")
if total_pnl is not None:
    pnl_sign = "+" if total_pnl >= 0 else ""
    k2.metric("總損益", f"{pnl_sign}{total_pnl:,.0f}",
              delta=f"{total_pnl/total_value*100:.1f}%" if total_value else None)
else:
    k2.metric("總損益", "N/A")
k3.metric("持倉數量", len(full_df))
k4.metric("平台數", full_df["platform"].nunique())

st.markdown("---")

# ── 圖表 ──
by_platform = full_df.groupby("platform")["market_value"].sum().reset_index()
by_platform.columns = ["平台", "市值"]

c1, c2 = st.columns(2)
with c1:
    st.subheader("各平台分配")
    fig_pie = px.pie(by_platform, values="市值", names="平台",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("各平台市值")
    fig_bar = px.bar(by_platform.sort_values("市值"),
                     x="市值", y="平台", orientation="h",
                     color="平台",
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_bar.update_layout(showlegend=False, margin=dict(t=0, b=0),
                          yaxis_title=None, xaxis_title="市值")
    st.plotly_chart(fig_bar, use_container_width=True)

# ── 持倉明細 ──
st.subheader("持倉明細")
display_df = full_df.sort_values("market_value", ascending=False).copy()
display_df["佔比 %"] = (display_df["market_value"] / total_value * 100).round(1)
display_df["損益"] = display_df["pnl"].apply(
    lambda x: f"+{x:,.0f}" if pd.notna(x) and x >= 0 else (f"{x:,.0f}" if pd.notna(x) else "—")
)

show_cols = {
    "symbol": "代號", "name": "名稱", "platform": "平台",
    "qty": "數量", "current_price": "現價",
    "market_value": "市值", "currency": "幣種",
    "佔比 %": "佔比 %", "損益": "損益",
}
table = display_df[[c for c in show_cols if c in display_df.columns]].rename(columns=show_cols)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "市值": st.column_config.NumberColumn(format="%,.0f"),
        "佔比 %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
    },
)
