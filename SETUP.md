# 部署設定指南

兩個外部服務要設定，全部免費。約 10 分鐘。

---

## 1. Anthropic API Key（AI 摘要 — Claude Haiku）

1. 去 https://console.anthropic.com
2. 登入後左側 **API Keys** → **Create Key**
3. 複製 `sk-ant-...` 那串
4. 需要在 Billing 充值最少 $5（Haiku 成本極低，$5 約可跑 3000+ 篇摘要）

---

## 2. Supabase 資料庫（儲存 Portfolio + 摘要）

1. 去 https://supabase.com → Sign up（用 GitHub 登入最快）
2. 新建 project：
   - Name：`tiff-investment`（隨意）
   - Database password：隨機生成一個存好
   - Region：Tokyo（近港）
3. 等 1 分鐘建立完成
4. 左側 **SQL Editor** → **New query** → 貼入 `supabase_schema.sql` 的內容 → **Run**
5. 左側 **Project Settings → API** → 複製：
   - **Project URL**（`https://xxx.supabase.co`）
   - **anon public key**（`eyJ...` 很長一串）

---

## 3. 貼進 Streamlit Cloud Secrets

Streamlit Cloud → 你的 app → **Settings → Secrets**，貼入：

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

⚠️ **不要**加 `[auth]` / `[auth.google]` 區塊 — 那會啟動 Streamlit 原生 auth，把整個 app 鎖住。本 app 用自己的 email 輸入模式，不需要 Google OAuth。

儲存後 Streamlit 會自動重啟。**完成。**

---

## 4. Streamlit Cloud Sharing 設定

**一定要把 app 設成公開**：

1. Streamlit Cloud → 你的 app → **Settings → Sharing**
2. 「Who can view this app」選 **This app is public and searchable**
3. Save

---

## 測試流程

1. 開網站 → 看到「進入工具 / 輸入 email」
2. 輸入任一 email → 進入 Home 頁
3. 去 Portfolio → 上傳 CSV → 資料自動綁到 email
4. **關閉網站，再打開、再輸入同一 email** → 看到上次的 portfolio
5. 去市場日報 → 一鍵摘要 → 摘要自動保存
