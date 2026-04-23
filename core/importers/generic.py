"""通用 CSV 匯入器（Syfe / StashAway / Jarsy / 其他）"""
import pandas as pd


class GenericImporter:
    platform = "其他"

    # 可能的欄位名稱對應（兼容多種格式）
    SYMBOL_COLS = ["symbol", "ticker", "asset", "fund", "stock", "code", "security", "名稱", "基金", "代號"]
    QTY_COLS = ["qty", "quantity", "units", "shares", "holdings", "數量", "單位數"]
    VALUE_COLS = ["market_value", "value", "total_value", "market value", "usd value", "總值", "市值"]
    PRICE_COLS = ["current_price", "price", "nav", "close_price", "last_price", "現價", "淨值"]

    def __init__(self, filepath: str, platform_name: str = None):
        self.filepath = filepath
        if platform_name:
            self.platform = platform_name

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        return self._normalize(df)

    def _find_col(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        lower_cols = {c.lower(): c for c in df.columns}
        for candidate in candidates:
            if candidate.lower() in lower_cols:
                return lower_cols[candidate.lower()]
        return None

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        result = pd.DataFrame()

        sym_col = self._find_col(df, self.SYMBOL_COLS)
        qty_col = self._find_col(df, self.QTY_COLS)
        val_col = self._find_col(df, self.VALUE_COLS)
        price_col = self._find_col(df, self.PRICE_COLS)

        result["symbol"] = df[sym_col] if sym_col else df.iloc[:, 0]
        result["name"] = result["symbol"]
        result["qty"] = pd.to_numeric(
            df[qty_col].astype(str).str.replace(",", "") if qty_col else None, errors="coerce"
        )
        result["market_value"] = pd.to_numeric(
            df[val_col].astype(str).str.replace(",", "") if val_col else None, errors="coerce"
        )
        result["current_price"] = pd.to_numeric(
            df[price_col].astype(str).str.replace(",", "") if price_col else None, errors="coerce"
        )
        result["cost_price"] = None
        result["pnl"] = None
        result["currency"] = "USD"
        result["platform"] = self.platform

        return result[result["symbol"].notna()].reset_index(drop=True)
