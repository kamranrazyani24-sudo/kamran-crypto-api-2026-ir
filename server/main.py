import os
import asyncio
import requests
import pandas as pd
import numpy as np
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn

# --- تنظیمات اصلی ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

app = FastAPI()

# --- تابع هوشمند دریافت داده از CoinEx (جایگزین بایننس) ---
def get_crypto_data(symbol):
    try:
        # تبدیل نام ارز به فرمت کوین‌اکس (مثلاً BTCUSDT)
        clean_symbol = symbol.upper().replace("USDT", "") + "USDT"
        url = f"https://api.coinex.com/v1/market/kline?market={clean_symbol}&type=1hour&limit=100"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                # قیمت‌های بسته شدن (Close Prices)
                prices = [float(item[3]) for item in data["data"]]
                return prices
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# --- بخش تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز! نام ارز دیجیتال مورد نظرت را بفرست تا تحلیلش کنم (مثلاً BTC یا ADA)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    await update.message.reply_text(f"🔍 در حال دریافت داده‌های {symbol} از CoinEx و تحلیل الگوها... لطفا صبر کنید.")
    
    prices = get_crypto_data(symbol)
    
    if prices:
        current_price = prices[-1]
        # در اینجا می‌توانید توابع تحلیل الگو را صدا بزنید
        # فعلاً یک پاسخ ساده برای تست سلامت ربات:
        await update.message.reply_text(f"✅ داده‌های {symbol} دریافت شد.\n💰 قیمت فعلی: {current_price:.2f} USDT\n📈 وضعیت: در حال پردازش الگوهای تکنیکال...")
    else:
        await update.message.reply_text("❌ خطا: متأسفانه داده‌ای دریافت نشد. مطمئن شوید نام ارز را درست وارد کرده‌اید.")

# --- تنظیمات FastAPI و اجرای ربات ---
@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

async def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # اجرای تلگرام در کنار FastAPI
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(1)

if name == "main":
    # اجرای همزمان وب‌سرور و ربات تلگرام
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    uvicorn.run(app, host="0.0.0.0", port=PORT)
