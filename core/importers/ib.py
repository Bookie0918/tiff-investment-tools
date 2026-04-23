"""Interactive Brokers Activity Statement CSV 匯入器"""
import pandas as pd
import re


class IBImporter:
    platform = "Interactive Brokers"

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        # IB CSV 有多個 section，先找 Open Positions 那段
        with open(self.filepath, encoding="utf-8-sig") as f:
            lines = f.readlines()

        # 找 "Open Positions" section
        section_start = None
        for i, line in enumerate(lines):
            if line.startswith("Open Positions,Header,") or "Open Positions" in line and "Symbol" in line:
                section_start = i
                break

        if section_start is None:
            # fallback：當成普通 CSV 讀取
            df = pd.read_csv(self.filepath, encoding="utf-8-sig")
            return self._normalize_generic(df)

        # 收集 Data 行
        rows = []
        headers = None
        for line in lines[section_start:]:
            if line.startswith("Open Positions,Header,"):
                headers = [h.strip() for h in line.split(",")[2:]]
            elif line.startswith("Open Positions,Data,") and headers:
                values = [v.strip() for v in line.split(",")[2:]]
                rows.append(dict(zip(headers, values)))
            elif line.startswith("Open Positions,") and "Total" in line:
                break

        if not rows:
            df = pd.read_csv(self.filepath, encoding="utf-8-sig")
            return self._normalize_generic(df)

        df = pd.DataFrame(rows)
        return self._normalize(df)

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        col_map = {
            "Symbol": "symbol", "Description": "name",
            "Quantity": "qty", "Cost Price": "cost_price",
            "Close Price": "current_price", "Value": "market_value",
            "Unrealized P/L": "pnl", "Currency": "currency",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        for col in ["qty", "cost_price", "current_price", "market_value", "pnl"]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ""),
                    errors="coerce"
                )

        df["platform"] = self.platform
        if "name" not in df.columns:
            df["name"] = df.get("symbol", "")
        return df[df["symbol"].notna()].reset_index(drop=True)

    def _normalize_generic(self, df: pd.DataFrame) -> pd.DataFrame:
        df["platform"] = self.platform
        df["currency"] = "USD"
        return df
