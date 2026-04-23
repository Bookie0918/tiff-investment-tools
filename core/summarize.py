"""AI 摘要：優先用 Claude Haiku，fallback 到 Ollama（本地）"""
import os
import requests
from core.config import SUMMARY_PROMPT

CLAUDE_MODEL = "claude-haiku-4-5"


def _get_api_key() -> str | None:
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


def summarize_claude(article: dict, api_key: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    prompt = SUMMARY_PROMPT.format(
        title=article["title"],
        source=article["source_name"],
        content=(article.get("content") or "")[:1200],
    )
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def summarize_ollama(article: dict) -> str:
    prompt = SUMMARY_PROMPT.format(
        title=article["title"],
        source=article["source_name"],
        content=(article.get("content") or "")[:1200],
    )
    try:
        import json
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:14b", "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.3, "num_predict": 400}},
            timeout=90,
        )
        data = json.loads(resp.text)
        return data.get("response", "").strip()
    except Exception as e:
        return f"[摘要失敗: {e}]"


def summarize(article: dict) -> str:
    api_key = _get_api_key()
    if api_key:
        try:
            return summarize_claude(article, api_key)
        except Exception as e:
            return f"[Claude API 錯誤: {type(e).__name__} — {str(e)[:200]}]"
    try:
        requests.get("http://localhost:11434/api/tags", timeout=1)
        return summarize_ollama(article)
    except Exception:
        return "[未設定 AI 後端：請在 Streamlit Cloud Secrets 加入 ANTHROPIC_API_KEY]"


def has_ai() -> bool:
    if _get_api_key():
        return True
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False
