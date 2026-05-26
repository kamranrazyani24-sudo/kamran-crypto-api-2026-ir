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
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1h&limit=100"
        res = requests.get(url).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'q_vol', 'trades', 'tb_base', 'tb_quote', 'ignore'])
        return df['close'].astype(float).tolist()
    except:
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
    await update.message.reply_text(f"🔍 در حال تحلیل {symbol}...")
    prices = await get_crypto_data(symbol)
    result = analyze_pattern(prices)
    await update.message.reply_text(result)

# --- اجرای همزمان وب‌سرور و ربات ---
async def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())

if name == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
