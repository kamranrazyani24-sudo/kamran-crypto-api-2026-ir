import os
import asyncio
import uvicorn
from fastapi import FastAPI
from bots.telegram_bot import run_bot
import multiprocessing

app = FastAPI(title="Crypto Pattern Bot")

@app.get("/")
def root():
    return {"status": "ok", "message": "Bot and API are running"}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    return {"status": "ok", "symbol": symbol, "message": "Analysis ready"}

# ---------------------------------------------------------
# راه حل: اجرای همزمان با استفاده از یک پروسه جداگانه
# ---------------------------------------------------------
def run_all():
    # اجرای ربات
    bot_process = multiprocessing.Process(target=lambda: asyncio.run(run_bot()))
    bot_process.start()
    
    # اجرای وب‌سرور در ترد اصلی
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_all()
