"""AI 摘要：優先用 Gemini Flash（免費），fallback 到 Ollama（本地）"""
import os
import requests
from core.config import SUMMARY_PROMPT


def _get_api_key() -> str | None:
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    except Exception:
        return os.environ.get("GEMINI_API_KEY")


def summarize_gemini(article: dict, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = SUMMARY_PROMPT.format(
        title=article["title"],
        source=article["source_name"],
        content=(article.get("content") or "")[:1200],
    )
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.3, "max_output_tokens": 400},
    )
    return response.text.strip()


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
            return summarize_gemini(article, api_key)
        except Exception:
            pass
    return summarize_ollama(article)


def has_ai() -> bool:
    if _get_api_key():
        return True
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False
