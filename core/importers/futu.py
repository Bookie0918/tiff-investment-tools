"""富途 / Moomoo CSV 持倉匯入器"""
import pandas as pd
from pathlib import Path


class FutuImporter:
    platform = "富途 Futu"

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        return self._normalize(df)

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        # 富途持倉匯出欄位：股票代號 / 股票名稱 / 數量 / 成本價 / 現價 / 市值 / 盈虧 / 回報率
        col_map = {
            # 中文版
            "股票代號": "symbol", "股票名稱": "name", "數量": "qty",
            "成本價": "cost_price", "現價": "current_price",
            "市值": "market_value", "盈虧": "pnl", "回報率": "return_pct",
            # 英文版
            "Symbol": "symbol", "Stock Name": "name", "Quantity": "qty",
            "Avg Cost": "cost_price", "Latest Price": "current_price",
            "Market Value": "market_value", "Unrealized P/L": "pnl",
            "Return": "return_pct",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        for col in ["qty", "cost_price", "current_price", "market_value", "pnl", "return_pct"]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "").str.replace("%", ""),
                    errors="coerce"
                )

        df["platform"] = self.platform
        df["currency"] = df.get("currency", df.get("Currency", "HKD"))
        return df[df["symbol"].notna()].reset_index(drop=True)
