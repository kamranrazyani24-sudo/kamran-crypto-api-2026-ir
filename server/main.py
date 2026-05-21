import os
import threading
import requests
from fastapi import FastAPI, HTTPException

from server.data_fetcher import get_klines
from server.patterns import extract_pattern
from server.similarity import similarity
from server import config
from bots.telegram_bot import run_bot

app = FastAPI(title="Crypto Pattern Bot")

# -------------------------------
# لیست جایگزین (چون بایننس روی رندر خطا داد)
# -------------------------------
def get_binance_symbols():
    # به دلیل خطای ۴۵۱ در رندر، از لیست دستی استفاده می‌کنیم
    # می‌توانید هر نمادی که می‌خواهید را اینجا اضافه کنید
    return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT"]

MARKET = get_binance_symbols()

# -----------------------------------------
# استارت ربات تلگرام (اصلاح شده برای ترد)
# -----------------------------------------
@app.on_event("startup")
def start_bot():
    # ایجاد یک ترد برای اجرای ربات بدون تداخل با سیگنال‌های سیستم
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("Telegram Bot started in background thread.")

@app.get("/")
def root():
    return {"status": "ok", "message": "Bot is running with Manual Symbol List", "total_symbols": len(MARKET)}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    # چک کردن ۹ کندل آخر
    try:
        candles = get_klines(symbol, config.TIMEFRAME, 9)
        if not candles or len(candles) < 9:
            raise HTTPException(status_code=404, detail="Not enough candle data")

        target_pattern = extract_pattern(candles)
        matches = []

        for market_symbol in MARKET:
            if market_symbol == symbol: continue
            c = get_klines(market_symbol, config.TIMEFRAME, 9)
            if not c or len(c) < 9: continue
            
            p = extract_pattern(c)
            score = similarity(target_pattern, p)
            if score >= config.SIMILARITY_THRESHOLD:
                matches.append({"symbol": market_symbol, "score": score})

        matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:config.MAX_MATCH]
        
        c6 = candles[6]
        direction = "bullish" if c6["close"] > c6["open"] else "bearish"

        return {"status": "ok", "symbol": symbol, "direction": direction, "matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
