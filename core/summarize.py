"""AI 摘要：優先用 Anthropic API（雲端），fallback 到 Ollama（本地）"""
import os
import requests
from core.config import SUMMARY_PROMPT


def _get_api_key() -> str | None:
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


def summarize_anthropic(article: dict, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    prompt = SUMMARY_PROMPT.format(
        title=article["title"],
        source=article["source_name"],
        content=(article.get("content") or "")[:1200],
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def summarize_ollama(article: dict) -> str:
    prompt = SUMMARY_PROMPT.format(
        title=article["title"],
        source=article["source_name"],
        content=(article.get("content") or "")[:1200],
    )
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:14b", "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.3, "num_predict": 400}},
            timeout=90,
        )
        import json
        data = json.loads(resp.text)
        return data.get("response", "").strip()
    except Exception as e:
        return f"[摘要失敗: {e}]"


def summarize(article: dict) -> str:
    api_key = _get_api_key()
    if api_key:
        try:
            return summarize_anthropic(article, api_key)
        except Exception:
            pass
    return summarize_ollama(article)


def has_ai() -> bool:
    """判斷是否有可用的 AI 後端"""
    if _get_api_key():
        return True
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False
