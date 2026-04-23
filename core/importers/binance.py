"""Binance 持倉 / 交易紀錄 CSV 匯入器"""
import pandas as pd


class BinanceImporter:
    platform = "Binance"

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()

        # 判斷是持倉快照還是交易記錄
        if "Coin" in df.columns and "Amount" in df.columns:
            return self._from_snapshot(df)
        elif "Pair" in df.columns and "Side" in df.columns:
            return self._from_trades(df)
        else:
            return self._normalize_generic(df)

    def _from_snapshot(self, df: pd.DataFrame) -> pd.DataFrame:
        """持倉快照格式：Coin / Amount / USD Value"""
        df = df.rename(columns={"Coin": "symbol", "Amount": "qty", "USD Value": "market_value"})
        df["name"] = df["symbol"]
        df["currency"] = "USD"
        df["cost_price"] = None
        df["current_price"] = None
        df["pnl"] = None
        df["return_pct"] = None
        df["platform"] = self.platform

        for col in ["qty", "market_value"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

        return df[df["symbol"].notna() & (df["qty"] > 0)].reset_index(drop=True)

    def _from_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """交易記錄格式：聚合成持倉"""
        df["Date"] = pd.to_datetime(df["Date(UTC)"], errors="coerce")
        df["Executed"] = pd.to_numeric(df["Executed"].astype(str).str.extract(r"([\d.]+)")[0], errors="coerce")
        df["base_asset"] = df["Pair"].str.extract(r"^([A-Z]+)")

        buy = df[df["Side"] == "BUY"].groupby("base_asset")["Executed"].sum()
        sell = df[df["Side"] == "SELL"].groupby("base_asset")["Executed"].sum()
        net = (buy - sell).fillna(buy).fillna(0)
        net = net[net > 0.000001]

        result = pd.DataFrame({
            "symbol": net.index,
            "name": net.index,
            "qty": net.values,
            "currency": "USD",
            "platform": self.platform,
            "market_value": None,
            "cost_price": None,
            "current_price": None,
            "pnl": None,
        })
        return result.reset_index(drop=True)

    def _normalize_generic(self, df: pd.DataFrame) -> pd.DataFrame:
        df["platform"] = self.platform
        df["currency"] = "USD"
        return df
