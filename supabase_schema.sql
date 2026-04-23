-- Supabase Schema：Tiff 投資研究工具
-- 在 Supabase Dashboard → SQL Editor 執行一次即可

-- 持倉表
CREATE TABLE IF NOT EXISTS holdings (
  id BIGSERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,
  batch_id UUID,
  symbol TEXT NOT NULL,
  name TEXT,
  qty NUMERIC,
  cost_price NUMERIC,
  current_price NUMERIC,
  market_value NUMERIC,
  pnl NUMERIC,
  currency TEXT,
  platform TEXT,
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_holdings_user ON holdings(user_email);
CREATE INDEX IF NOT EXISTS idx_holdings_uploaded_at ON holdings(uploaded_at DESC);

-- AI 摘要快取表
CREATE TABLE IF NOT EXISTS summaries (
  id BIGSERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,
  article_url TEXT NOT NULL,
  article_title TEXT,
  summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_email, article_url)
);
CREATE INDEX IF NOT EXISTS idx_summaries_user ON summaries(user_email);

-- Row Level Security（選用但建議）：只讓人讀自己的資料
ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;

-- 如果用 anon key（簡單起見），可以暫時用以下 policy（任何 anon 都能讀寫，
-- 配合應用端強制過濾 user_email 即可；正式環境建議用 service_role key 或 JWT）：
CREATE POLICY IF NOT EXISTS holdings_all ON holdings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS summaries_all ON summaries FOR ALL USING (true) WITH CHECK (true);
