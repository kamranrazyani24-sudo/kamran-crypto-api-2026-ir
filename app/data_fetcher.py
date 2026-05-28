import requests

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

def get_klines(symbol: str, interval: str, limit: int = 200):
    """
    Fetch OHLCV candles from Binance.
    Returns list format:
    [
      [open_time, open, high, low, close, volume, close_time, ...],
      ...
    ]
    """
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }

    r = requests.get(BINANCE_KLINES_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Basic validation
    if not isinstance(data, list):
        raise ValueError(f"Invalid kline response for {symbol} {interval}")

    return data
