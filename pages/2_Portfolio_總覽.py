import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
from pathlib import Path
from core.importers import auto_detect, FutuImporter, IBImporter, BinanceImporter, GenericImporter
from core.style import inject
from core.auth import require_login, sidebar_user_panel, is_auth_configured
from core import db

st.set_page_config(page_title="Portfolio 總覽", page_icon="💼", layout="wide")
inject()
st.title("Portfolio 總覽")

# ── 登入 ──
if is_auth_configured():
    email = require_login()
    sidebar_user_panel()
else:
    email = None

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

PALETTE = ["#8a6a10", "#b89048", "#7a7060", "#c4a661", "#968e7e", "#5a4a20"]

def detect_platform(filename: str):
    stem = Path(filename).stem.lower()
    for key, (name, cls) in PLATFORM_MAP.items():
        if key in stem:
            return name, cls
    return "其他", GenericImporter

def load_csv(uploaded_file):
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


def show_dashboard(full_df: pd.DataFrame):
    full_df["market_value"] = pd.to_numeric(full_df["market_value"], errors="coerce").fillna(0)
    full_df["pnl"] = pd.to_numeric(full_df["pnl"], errors="coerce")
    total_value = full_df["market_value"].sum()
    total_pnl = full_df["pnl"].sum() if full_df["pnl"].notna().any() else None

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

    by_platform = full_df.groupby("platform")["market_value"].sum().reset_index()
    by_platform.columns = ["平台", "市值"]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("各平台分配")
        fig_pie = px.pie(by_platform, values="市值", names="平台",
                         color_discrete_sequence=PALETTE, hole=0.5)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                              textfont=dict(color="#f4efe6", family="DM Sans, Noto Sans TC"))
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="DM Sans, Noto Sans TC", color="#1c1810"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("各平台市值")
        fig_bar = px.bar(by_platform.sort_values("市值"),
                         x="市值", y="平台", orientation="h",
                         color="平台", color_discrete_sequence=PALETTE)
        fig_bar.update_layout(showlegend=False, margin=dict(t=0, b=0),
                              yaxis_title=None, xaxis_title="市值",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="DM Sans, Noto Sans TC", color="#1c1810"))
        fig_bar.update_xaxes(gridcolor="#d5cfc4")
        st.plotly_chart(fig_bar, use_container_width=True)

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
        table, use_container_width=True, hide_index=True,
        column_config={
            "市值": st.column_config.NumberColumn(format="%,.0f"),
            "佔比 %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
        },
    )


# ── 資料源選擇 ──
saved_df = pd.DataFrame()
if email and db.is_configured():
    saved_df = db.load_holdings(email)

tab_upload, tab_saved = st.tabs(["上傳新資料", f"已保存資料 ({len(saved_df)} 筆)"])

# ── Tab 1：上傳 ──
with tab_upload:
    st.markdown("### 上傳持倉 CSV")
    st.caption("命名包含平台名即可自動識別：`futu_xxx.csv`、`binance_xxx.csv`、`ib_xxx.csv`、`syfe_xxx.csv`、`stashaway_xxx.csv`、`jarsy_xxx.csv`")

    uploaded_files = st.file_uploader(
        "選擇一個或多個 CSV 檔案", type="csv",
        accept_multiple_files=True, label_visibility="collapsed",
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

    if uploaded_files:
        frames = []
        for f in uploaded_files:
            df, platform = load_csv(f)
            if df is not None:
                st.success(f"✅ {f.name} → {platform}（{len(df)} 筆）")
                frames.append(df)

        if frames:
            full_df = pd.concat(frames, ignore_index=True)

            col_a, col_b = st.columns([1, 3])
            with col_a:
                save_to_db = st.checkbox("保存到帳號", value=bool(email and db.is_configured()),
                                         disabled=not (email and db.is_configured()))
            if save_to_db and email and db.is_configured():
                if st.button("保存並顯示", type="primary"):
                    try:
                        db.save_holdings(email, full_df, replace=True)
                        st.success("已保存。下次登入會自動載入。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失敗：{e}")
            st.markdown("---")
            show_dashboard(full_df)
    else:
        if saved_df.empty:
            st.info("👆 上傳 CSV 後顯示 Portfolio 總覽")

# ── Tab 2：已保存 ──
with tab_saved:
    if not email:
        st.info("登入後可保存 Portfolio 資料，下次自動載入。")
    elif not db.is_configured():
        st.warning("資料庫未設定，無法保存。")
    elif saved_df.empty:
        st.info("尚未保存任何 Portfolio 資料。去「上傳新資料」分頁試試。")
    else:
        last = db.last_upload_time(email)
        if last:
            st.caption(f"上次更新：{last.strftime('%Y-%m-%d %H:%M')}")
        col_d1, col_d2, _ = st.columns([1, 1, 3])
        with col_d1:
            if st.button("刪除所有保存資料"):
                db.save_holdings(email, pd.DataFrame(columns=REQUIRED_COLS), replace=True)
                st.rerun()
        st.markdown("---")
        show_dashboard(saved_df)
