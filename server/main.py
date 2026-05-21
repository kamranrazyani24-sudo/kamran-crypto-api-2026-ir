import os
import threading
import asyncio
import uvicorn
from fastapi import FastAPI
from bots.telegram_bot import run_bot

app = FastAPI(title="Crypto Pattern Bot")

# -----------------------------------------
# تابع اجرای ربات به صورت Async
# -----------------------------------------
def start_bot_in_thread():
    # چون run_bot یک تابع async است، باید اینجا از asyncio.run استفاده کنیم
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"Error in bot thread: {e}")

# -----------------------------------------
# استارت ربات در ترد جداگانه (قبل از اجرای سرور)
# -----------------------------------------
bot_thread = threading.Thread(target=start_bot_in_thread, daemon=True)
bot_thread.start()

# -----------------------------------------
# مسیرهای API
# -----------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "Bot and API are running"}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    # در اینجا منطق تحلیل خود را قرار می‌دهی
    return {"status": "ok", "symbol": symbol, "message": "Analysis ready"}

if __name__ == "__main__":
    # اجرا روی پورتی که Render اختصاص می‌دهد
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
