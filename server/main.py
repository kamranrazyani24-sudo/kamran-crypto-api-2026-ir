import os
import asyncio
import requests
import numpy as np
import pandas as pd
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

app = FastAPI()

# تابع تحلیل استراتژی کامران
def fetch_data(symbol):
    try:
        url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=1hour&limit=200"
        res = requests.get(url, timeout=10).json()
        if res.get("code") == 0:
            return pd.DataFrame(res["data"], columns=['time','open','close','high','low','vol','amt']).astype(float)
    except: return None

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = update.message.text.upper().strip().replace("USDT", "") + "USDT"
    msg = await update.message.reply_text(f"🔍 کامران جان، در حال واکاوی {coin}...")
    
    target_df = fetch_data(coin)
    if target_df is None or len(target_df) < 10:
        await msg.edit_text("❌ خطا در دریافت داده.")
        return

    target_norm = (target_df['close'].values[0:9] - np.mean(target_df['close'].values[0:9])) / (np.std(target_df['close'].values[0:9]) + 1e-9)
    matches = []

    for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]: # فعلاً ۵ ارز برای تست سریع
        df = fetch_data(s)
        if df is None: continue
        p = df['close'].values
        for i in range(len(p) - 10):
            w = (p[i:i+9] - np.mean(p[i:i+9])) / (np.std(p[i:i+9]) + 1e-9)
            if np.linalg.norm(target_norm - w) < 0.6:
                matches.append({'c': ((p[i+6]/p[i+5])-1)*100, 'b': p[i+6]>p[i+5]})

    if matches:
        res = f"✅ پیدا شد! {len(matches)} الگو.\nپیش‌بینی: {'صعودی 📈' if sum(m['c'] for m in matches)>0 else 'نزولی 📉'}"
        await msg.edit_text(res)
    else:
        await msg.edit_text("😔 الگوی مشابهی پیدا نشد.")

@app.on_event("startup")
async def startup():
    # راه‌اندازی ربات بدون مسدود کردن پورت وب
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("سلام کامران عزیز! نام ارز را بفرست:")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_analysis))
    await application.initialize()
    await application.start()
    asyncio.create_task(application.updater.start_polling())
    logger.info("Bot is polling...")

@app.get("/")
async def root(): return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
