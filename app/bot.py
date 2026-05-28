from typing import Dict, Any

from app.config import TOP_20_COINS
from app.data_fetcher import fetch_klines
from app.pattern import extract_pattern


def start() -> Dict[str, Any]:
    return {
