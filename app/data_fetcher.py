import requests

def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    return s + "USDT"


def get_klines(symbol: str, timeframe="1h", limit=200):
    timeframe = "1h"
    symbol = normalize_symbol(symbol)

    # CoinEx
    try:
        tf_map = {"1h": "1hour"}
        tf = tf_map["1h"]

        url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type={tf}&limit={limit}"
        r = requests.get(url, timeout=10).json()

        if r.get("code") == 0:
            closes = [float(x[2]) for x in r["data"]]
            if closes:
                return closes
    except:
        pass

    # BingX
    try:
        bingx_symbol = symbol.replace("USDT", "") + "-USDT"
        url = (
            "https://open-api.bingx.com/openApi/swap/v2/quote/klines"
            f"?symbol={bingx_symbol}&interval=1h&limit={limit}"
        )
        r = requests.get(url, timeout=10).json()

        if "data" in r:
            closes = []
            for item in r["data"]:
                if isinstance(item, list) and len(item) > 4:
                    closes.append(float(item[4]))
            if closes:
                return closes
    except:
        pass

    return None
