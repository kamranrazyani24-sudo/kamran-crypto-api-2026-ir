from typing import Dict, Any

from app.config import TOP_20_COINS
from app.data_fetcher import fetch_klines
from app.pattern import extract_pattern


def start() -> Dict[str, Any]:
    return {
        "status": "ok",
        "message": "Service started",
        "top_coins": TOP_20_COINS,
    }


def analyze(symbol: str = "ADA") -> Dict[str, Any]:
    symbol = symbol.upper()

    # نمونه‌ی ساده برای اینکه endpoint کار کند:
    candles = fetch_klines(symbol=symbol, timeframe="1M", limit=200)
    pattern = extract_pattern(candles)

    return {
        "status": "ok",
        "symbol": symbol,
        "timeframe": "1M",
        "pattern": pattern,
        "note": "This is package-based safe layout. Plug your full logic here.",
    }
