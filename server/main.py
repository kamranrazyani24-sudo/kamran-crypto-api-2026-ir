import os
import asyncio
import requests
import numpy as np
import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn
import logging

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Render پورت را به صورت خودکار به ما می‌دهد
PORT = int(os.environ.get("PORT", 10000))

app = FastAPI()

# استخر ۳۰ ارز برتر
SEARCH_POOL = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "DOGEUSDT", 
    "MATICUSDT", "LINKUSDT", "SHIBUSDT", "LTCUSDT", "TRXUSDT", "NEARUSDT", "ATOMUSDT", "UNIUSDT", 
    "XLMUSDT", "ETCUSDT", "FILUSDT", "LDOUSDT", "APTUSDT", "OPUSDT", "ARBUSDT", "TIAUSDT", "RNDRUSDT",
    "STXUSDT", "INJUSDT", "KASUSDT", "FETUSDT"
]

def fetch_data(symbol, limit=250):
    try:
        url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=1hour&limit={limit}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                df = pd.DataFrame(data["data"], columns=['time', 'open', 'close', 'high', 'low', 'volume', 'amount'])
                return df.astype(float)
        return None
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def normalize(data):
    return (data - np.mean(data)) / (np.std(data) + 1e-9)

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.upper().strip().replace("USDT", "")
    target_coin = user_input + "USDT"
    status_msg = await update.message.reply_text(f"🔍 کامران جان، در حال تحلیل {target_coin}...")

    target_df = fetch_data(target_coin, limit=10)
    if target_df is None or len(target_df) < 10:
        await status_msg.edit_text("❌ خطا در دریافت داده.")
        return

    target_pattern = target_df['close'].values[0:9] 
    target_norm = normalize(target_pattern)
    found_matches = []

    for symbol in SEARCH_POOL:
        source_df = fetch_data(symbol, limit=200)
        if source_df is None: continue
        prices = source_df['close'].values
        for i in range(len(prices) - 10):
            window = prices[i : i+9]
            window_norm = normalize(window)
            if np.linalg.norm(target_norm - window_norm) < 0.5:
                found_matches.append({'change': ((prices[i+6]/prices[i+5])-1)*100, 'bull': prices[i+6]>prices[i+5]})

    if found_matches:
        total = len(found_matches)
        bulls = sum(1 for m in found_matches if m['bull'])
        avg_move = sum(m['change'] for m in found_matches) / total
        direction = "صعودی 📈" if avg_move > 0 else "نزولی 📉"
        res = f"✅ **نتیجه V4:**\nتعداد الگو: `{total}`\n🟢 مثبت: {bulls} | 🔴 منفی: {total-bulls}\n🎯 پیش‌بینی: **{direction}**\nشدت: `{avg_move:.2f}%`"
        await status_msg.edit_text(res, parse_mode='Markdown')
    else:
        await status_msg.edit_text("😔 الگویی پیدا نشد.")

# تابع اجرای ربات
async def run_bot():
    if not TOKEN:
        logger.error("TOKEN MISSING")
        return
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("سلام کامران عزیز! نام ارز را بفرست:")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_analysis))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("Bot Polling Started")

@app.on_event("startup")
async def startup_event():
    # اجرای ربات در پس‌زمینه بدون بلاک کردن پورت وب
    asyncio.create_task(run_bot())

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
