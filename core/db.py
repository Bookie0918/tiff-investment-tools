"""Supabase 資料庫：儲存 portfolio holdings + AI 摘要"""
import os
import uuid
import pandas as pd
import streamlit as st
from datetime import datetime, timezone


def _get_secret(key: str) -> str | None:
    try:
        return st.secrets.get(key) or os.environ.get(key)
    except Exception:
        return os.environ.get(key)


@st.cache_resource
def _client():
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_KEY")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def is_configured() -> bool:
    return _client() is not None


# ── Holdings（持倉）──

def save_holdings(user_email: str, df: pd.DataFrame, replace: bool = True):
    """儲存一批 holdings。replace=True 會先刪除該 user 舊資料"""
    client = _client()
    if not client:
        raise RuntimeError("Supabase 未設定")
    if replace:
        client.table("holdings").delete().eq("user_email", user_email).execute()

    batch_id = str(uuid.uuid4())
    rows = []
    for _, r in df.iterrows():
        def _num(v):
            return float(v) if pd.notna(v) else None
        rows.append({
            "user_email": user_email,
            "batch_id": batch_id,
            "symbol": str(r.get("symbol", ""))[:50],
            "name": str(r.get("name", ""))[:200] if pd.notna(r.get("name")) else None,
            "qty": _num(r.get("qty")),
            "cost_price": _num(r.get("cost_price")),
            "current_price": _num(r.get("current_price")),
            "market_value": _num(r.get("market_value")),
            "pnl": _num(r.get("pnl")),
            "currency": str(r.get("currency", ""))[:10] if pd.notna(r.get("currency")) else None,
            "platform": str(r.get("platform", ""))[:50],
        })
    if rows:
        client.table("holdings").insert(rows).execute()
    return batch_id


def load_holdings(user_email: str) -> pd.DataFrame:
    """讀取使用者的 holdings"""
    client = _client()
    if not client:
        return pd.DataFrame()
    resp = (client.table("holdings")
            .select("symbol,name,qty,cost_price,current_price,market_value,pnl,currency,platform,uploaded_at")
            .eq("user_email", user_email)
            .order("market_value", desc=True)
            .execute())
    if not resp.data:
        return pd.DataFrame()
    return pd.DataFrame(resp.data)


def last_upload_time(user_email: str) -> datetime | None:
    client = _client()
    if not client:
        return None
    resp = (client.table("holdings").select("uploaded_at")
            .eq("user_email", user_email)
            .order("uploaded_at", desc=True).limit(1).execute())
    if resp.data:
        return datetime.fromisoformat(resp.data[0]["uploaded_at"].replace("Z", "+00:00"))
    return None


# ── Summaries（AI 摘要快取）──

def save_summary(user_email: str, article_url: str, article_title: str, summary: str):
    client = _client()
    if not client:
        return
    client.table("summaries").upsert({
        "user_email": user_email,
        "article_url": article_url,
        "article_title": article_title[:500],
        "summary": summary,
    }, on_conflict="user_email,article_url").execute()


def load_summaries(user_email: str) -> dict[str, str]:
    """回傳 {article_url: summary}"""
    client = _client()
    if not client:
        return {}
    resp = (client.table("summaries").select("article_url,summary")
            .eq("user_email", user_email).execute())
    return {r["article_url"]: r["summary"] for r in (resp.data or [])}


def clear_summaries(user_email: str):
    client = _client()
    if not client:
        return
    client.table("summaries").delete().eq("user_email", user_email).execute()
