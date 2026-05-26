import os
import asyncio
import pandas as pd
import numpy as np
import requests
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn

# --- تنظیمات اولیه ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

# --- منطق تحلیل بازار (V4) ---
async def get_crypto_data(symbol):
    try:
        s = symbol.strip().upper()

        # اگر کاربر جفت‌ارز کامل داد (مثلاً ADAUSDT) همان را استفاده کن
        # اگر فقط نام کوین داد (مثلاً ADA) تبدیلش کن به ADAUSDT
        if not s.endswith("USDT"):
            s = f"{s}USDT"

        url = f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1h&limit=100"

        res = requests.get(url, timeout=15).json()

        # اگر بایننس خطا بده، معمولاً dict برمی‌گردونه نه list
        if isinstance(res, dict) and "code" in res:
            # برای دیباگ در لاگ‌های Render خیلی کمک می‌کنه:
            print("Binance error:", res)
            return None

        df = pd.DataFrame(
            res,
            columns=["time","open","high","low","close","vol","close_time","q_vol","trades","taker_base","taker_quote","ignore"]
        )
        return df["close"].astype(float).tolist()

    except Exception as e:
        print("get_crypto_data exception:", repr(e))
        return None

def analyze_pattern(prices):
    # یک تحلیل ساده الگو برای تست (در نسخه اصلی پیچیده‌تر است)
    if not prices: return "خطا در دریافت داده"
    change = ((prices[-1] - prices[0]) / prices[0]) * 100
    if change > 2: return f"🚀 الگوی صعودی تشخیص داده شد. رشد: {change:.2f}%"
    elif change < -2: return f"⚠️ الگوی نزولی تشخیص داده شد. ریزش: {change:.2f}%"
    else: return "📉 بازار در وضعیت رنج (Neutral) قرار دارد."

# --- هندلرهای تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلام کامران عزیز! 🌹\nمن ربات V4 هستم. نام ارز را بفرست (مثلاً BTC)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    print(f"Received symbol: {symbol}") # این در لاگ‌های رندر چاپ می‌شود
    await update.message.reply_text(f"در حال تحلیل {symbol} هستم، لطفا صبر کنید...")
    
    try:
        prices = await get_crypto_data(symbol)
        if prices is None or len(prices) == 0:
            await update.message.reply_text("خطا: داده‌ای از بایننس دریافت نشد.")
            return
            
        result = analyze_pattern(prices)
        await update.message.reply_text(result)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("متاسفانه در تحلیل خطایی رخ داد.")

# --- اجرای همزمان وب‌سرور و ربات ---
async def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
