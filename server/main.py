import os
import threading
import uvicorn
from fastapi import FastAPI
from server.data_fetcher import get_klines
from server.patterns import extract_pattern
from server.similarity import similarity
from server import config
from bots.telegram_bot import run_bot

app = FastAPI(title="Crypto Pattern Bot")

# نمادهای دستی برای جلوگیری از خطای 451
MARKET = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT"]

# -----------------------------------------
# شروع ربات به روش کاملاً جداگانه
# -----------------------------------------
def start_bot_thread():
    print(">>> تلاش برای استارت ربات تلگرام در ترد جداگانه...")
    run_bot()

# اجرای ربات قبل از شروع وب‌سرور
bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
bot_thread.start()

@app.get("/")
def root():
    return {"status": "ok", "message": "Bot is running"}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    # کدهای قبلی پیش‌بینی (همان کدهایی که داشتی را اینجا بگذار)
    # برای کوتاه شدن پیام، اینجا فعلاً فقط تایید سلامت را می‌گذاریم
    return {"status": "ok", "symbol": symbol, "message": "API working"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
