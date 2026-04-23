from .futu import FutuImporter
from .ib import IBImporter
from .binance import BinanceImporter
from .generic import GenericImporter

IMPORTERS = {
    "futu": FutuImporter,
    "ib": IBImporter,
    "binance": BinanceImporter,
    "generic": GenericImporter,
}

def auto_detect(filepath: str):
    """根據 CSV 欄位自動判斷平台，回傳對應 importer class"""
    import csv
    try:
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = [h.strip().lower() for h in next(reader)]
    except Exception:
        return GenericImporter

    header_str = " ".join(headers)

    if "pair" in header_str and "executed" in header_str:
        return BinanceImporter
    if "coin" in header_str and ("usd value" in header_str or "btc value" in header_str):
        return BinanceImporter
    if "asset category" in header_str or "t. price" in header_str:
        return IBImporter
    if "股票代號" in header_str or "交易方向" in header_str or "order id" in header_str:
        return FutuImporter
    return GenericImporter
