import os
import threading
import requests
from fastapi import FastAPI, HTTPException

from server.data_fetcher import get_klines
from server.patterns import extract_pattern
from server.similarity import similarity
from server import config
from bots.telegram_bot import run_bot


app = FastAPI(title="Crypto Pattern Bot – Auto Market Symbols")


# -------------------------------
#   دریافت نمادهای فعال بایننس
# -------------------------------
def get_binance_symbols():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        symbols = []

        for s in data.get("symbols", []):
            if (
                s.get("status") == "TRADING"
                and s.get("quoteAsset") == "USDT"
                and not s.get("symbol").endswith("UPUSDT")
                and not s.get("symbol").endswith("DOWNUSDT")
            ):
                symbols.append(s["symbol"])

        print(f"Loaded {len(symbols)} symbols from Binance.")
        return symbols

    except Exception as e:
        print("Error loading Binance symbols:", e)
        return []


# دریافت لیست نمادها یکبار هنگام شروع
MARKET = get_binance_symbols()


# -----------------------------------------
#   استارت ربات تلگرام در یک ترد جداگانه
# -----------------------------------------
@app.on_event("startup")
def start_bot():
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("Telegram Bot started.")


# --------------------
#      Root Route
# --------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Crypto Pattern Bot with Auto-Binance Symbols is running",
        "total_symbols": len(MARKET)
    }


# --------------------
#   Prediction API
# --------------------
@app.get("/predict/{symbol}")
def predict(symbol: str):

    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    # چک اگر نماد در لیست صرافی باشه
    if symbol not in MARKET:
        raise HTTPException(status_code=400, detail="Symbol not found in Binance market list")

    # دریافت ۹ کندل آخر
    candles = get_klines(symbol, config.TIMEFRAME, 9)
    if not candles or len(candles) < 9:
        raise HTTPException(status_code=404, detail="Not enough candle data")

    # استخراج الگوی هدف
    target_pattern = extract_pattern(candles)

    matches = []

    for market_symbol in MARKET:
        if market_symbol == symbol:
            continue

        c = get_klines(market_symbol, config.TIMEFRAME, 9)
        if not c or len(c) < 9:
            continue

        p = extract_pattern(c)
        score = similarity(target_pattern, p)

        if score >= config.SIMILARITY_THRESHOLD:
            matches.append({"symbol": market_symbol, "score": score})

    # مرتب‌سازی بر اساس شباهت
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)
    matches = matches[:config.MAX_MATCH]

    if len(matches) < config.MIN_MATCH:
        return {"status": "ok", "prediction": "not_enough_matches"}

    # تعیین جهت حرکت کندلی
    c6 = candles[6]
    direction = "bullish" if c6["close"] > c6["open"] else "bearish"

    return {
        "status": "ok",
        "symbol": symbol,
        "direction": direction,
        "matches": matches
    }


# --------------------
#   Uvicorn Launcher
# --------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
