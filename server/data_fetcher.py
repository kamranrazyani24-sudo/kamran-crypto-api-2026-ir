import requests

BASE_URL = "https://api.binance.com/api/v3/klines"

def get_klines(symbol, interval="1h", limit=50):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    candles = []
    for c in data:
        candles.append({
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        })
    return candles
