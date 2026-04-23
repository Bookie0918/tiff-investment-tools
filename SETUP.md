# 部署設定指南

三個外部服務要設定，全部免費。約 15 分鐘。

---

## 1. Gemini API Key（AI 摘要）

1. 去 https://aistudio.google.com
2. 用 Google 帳號登入
3. 左上角「**Get API key**」→「Create API key」
4. 複製那串 `AIza...`

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

## 3. Google OAuth（登入）

1. 去 https://console.cloud.google.com
2. 建立專案：`tiff-investment`（或選現有專案）
3. 左側選單 → **APIs & Services → OAuth consent screen**
   - User Type：External
   - App name：Tiff 投資研究工具
   - Support email：你的 email
   - Authorized domains：`streamlit.app`
   - Scopes：加入 `openid`, `email`, `profile`
4. 左側 **Credentials → Create Credentials → OAuth client ID**
   - Application type：Web application
   - Authorized redirect URIs：加入
     ```
     https://tiff-investment-tools.streamlit.app/oauth2callback
     ```
     （把 domain 換成你的 Streamlit URL）
5. 建好後複製：
   - **Client ID**
   - **Client secret**

---

## 4. 貼進 Streamlit Cloud Secrets

Streamlit Cloud → 你的 app → **Settings → Secrets**，貼入：

```toml
GEMINI_API_KEY = "AIza..."
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJ..."

[auth]
redirect_uri = "https://tiff-investment-tools.streamlit.app/oauth2callback"
cookie_secret = "隨機生成一串，至少 32 字"

[auth.google]
client_id = "xxx.apps.googleusercontent.com"
client_secret = "GOCSPX-xxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

`cookie_secret` 生成：
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

儲存後 Streamlit 會自動重啟。**完成。**

---

## 測試流程

1. 開網站 → 看到「使用 Google 登入」
2. 登入 → 看到 Home 頁「歡迎，你的名字」
3. 去 Portfolio → 上傳 CSV → 勾選「保存到帳號」→ 按「保存並顯示」
4. **關閉網站，再打開、再登入** → 看到「已保存資料」頁保留了上次的 portfolio
5. 去市場日報 → AI 摘要 → 關閉再打開登入 → 摘要還在
