import os
import asyncio
import requests
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn

# --- تنظیمات اصلی ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

app = FastAPI()

# --- تابع دریافت داده از CoinEx (جایگزین بایننس برای پایداری در ایران) ---
def get_crypto_data(symbol):
    try:
        clean_symbol = symbol.upper().replace("USDT", "") + "USDT"
        url = f"https://api.coinex.com/v1/market/kline?market={clean_symbol}&type=1hour&limit=100"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                prices = [float(item[3]) for item in data["data"]]
                return prices
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# --- بخش تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز! نام ارز (مثلا BTC) را بفرست تا تحلیلش کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    await update.message.reply_text(f"🔍 در حال تحلیل {symbol} از منبع CoinEx...")
    
    prices = get_crypto_data(symbol)
    if prices:
        current_price = prices[-1]
        await update.message.reply_text(f"✅ داده دریافت شد.\n💰 قیمت فعلی {symbol}: {current_price:.2f} USDT")
    else:
        await update.message.reply_text("❌ خطا در دریافت داده. نام ارز را چک کنید.")

# --- اجرای FastAPI و ربات ---
@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

async def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(1)

# اصلاح حیاتی این خط:
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    uvicorn.run(app, host="0.0.0.0", port=PORT)
