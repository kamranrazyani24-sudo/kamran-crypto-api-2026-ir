import requests
from typing import List, Optional


def normalize_symbol(symbol: str) -> str:
    """
    تبدیل نماد ورودی به فرمت استاندارد
    مثال:
    BTC -> BTCUSDT
    btcusdt -> BTCUSDT
    ETH -> ETHUSDT
    """
    s = symbol.strip().upper()
    if s.endswith("USDT"):
        return s
    return s + "USDT"


def get_klines(symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[List[float]]:
    """
    دریافت قیمت‌های close برای تحلیل تکنیکال

    اولویت:
    1) CoinEx
    2) BingX

    خروجی:
    - لیستی از قیمت‌های close
    - در صورت خطا: None
    """
    clean_symbol = normalize_symbol(symbol)

    # -----------------------------
    # 1) CoinEx
    # -----------------------------
    try:
        # CoinEx timeframes نمونه: 1hour, 5min, 15min, 30min, 1day
        coinex_tf_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "1hour",
            "4h": "4hour",
            "1d": "1day",
        }
        coinex_timeframe = coinex_tf_map.get(timeframe, "1hour")

        url = (
            f"https://api.coinex.com/v1/market/kline"
            f"?market={clean_symbol}&type={coinex_timeframe}&limit={limit}"
        )

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # CoinEx معمولاً code == 0 در پاسخ موفق
            if isinstance(data, dict) and data.get("code") == 0 and "data" in data:
                klines = data["data"]

                # ساختار رایج: [timestamp, open, close, high, low, volume, amount]
                # اما برای اطمینان close را از اندیس 2 می‌گیریم
                closes = []
                for item in klines:
                    if isinstance(item, list) and len(item) > 2:
                        closes.append(float(item[2]))

                if closes:
                    print(f"[INFO] Data fetched from CoinEx: {clean_symbol}")
                    return closes

    except Exception as e:
        print(f"[ERROR] CoinEx fetch failed for {clean_symbol}: {e}")

    # -----------------------------
    # 2) BingX
    # -----------------------------
    try:
        # BingX معمولاً فرمت سمبل را با خط تیره می‌پذیرد
        bingx_symbol = clean_symbol.replace("USDT", "") + "-USDT"

        bingx_tf_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }
        bingx_timeframe = bingx_tf_map.get(timeframe, "1h")

        url = (
            f"https://open-api.bingx.com/openApi/swap/v2/quote/klines"
            f"?symbol={bingx_symbol}&interval={bingx_timeframe}&limit={limit}"
        )

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # ساختار پاسخ BingX ممکن است data["data"] باشد
            if isinstance(data, dict) and "data" in data and data["data"]:
                klines = data["data"]

                closes = []
                for item in klines:
                    # اگر به صورت لیست باشد معمولاً close در اندیس 4 یا 2 است بسته به endpoint
                    if isinstance(item, list):
                        if len(item) > 4:
                            closes.append(float(item[4]))
                        elif len(item) > 2:
                            closes.append(float(item[2]))
                    elif isinstance(item, dict) and "c" in item:
                        closes.append(float(item["c"]))

                if closes:
                    print(f"[INFO] Data fetched from BingX: {bingx_symbol}")
                    return closes

    except Exception as e:
        print(f"[ERROR] BingX fetch failed for {clean_symbol}: {e}")

    print(f"[WARN] No market data found for {clean_symbol}")
    return None
