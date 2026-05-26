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

# تنظیمات لاگ برای مشاهده وضعیت در Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت توکن و پورت از تنظیمات Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

app = FastAPI()

# استخر ۳۰ ارز برتر برای پیدا کردن شباهت رفتار طبق استراتژی کامران
SEARCH_POOL = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "DOGEUSDT", 
    "MATICUSDT", "LINKUSDT", "SHIBUSDT", "LTCUSDT", "TRXUSDT", "NEARUSDT", "ATOMUSDT", "UNIUSDT", 
    "XLMUSDT", "ETCUSDT", "FILUSDT", "LDOUSDT", "APTUSDT", "OPUSDT", "ARBUSDT", "TIAUSDT", "RNDRUSDT",
    "STXUSDT", "INJUSDT", "KASUSDT", "FETUSDT"
]

def fetch_data(symbol, limit=250):
    """دریافت داده از کوین‌اکس"""
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
    """نرمال‌سازی برای مقایسه شکل موج (مستقل از قیمت عددی)"""
    return (data - np.mean(data)) / (np.std(data) + 1e-9)

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.upper().strip().replace("USDT", "")
    target_coin = user_input + "USDT"
    
    status_msg = await update.message.reply_text(f"🔍 کامران جان، در حال واکاوی الگو در بازار برای {target_coin} هستم...")

    target_df = fetch_data(target_coin, limit=10)
    if target_df is None or len(target_df) < 10:
        await status_msg.edit_text("❌ خطا! داده‌ای دریافت نشد. نام ارز را درست وارد کردی؟ (مثال: BTC)")
        return

    # استخراج ۹ کندل اخیر (کندل ۱ تا ۹)
    target_pattern = target_df['close'].values[0:9] 
    target_norm = normalize(target_pattern)

    found_matches = []

    # جستجو در تاریخچه ۳۰ ارز
    for symbol in SEARCH_POOL:
        source_df = fetch_data(symbol, limit=250)
        if source_df is None: continue
        
        prices = source_df['close'].values
        for i in range(len(prices) - 10):
            window = prices[i : i+9]
            window_norm = normalize(window)
            
            distance = np.linalg.norm(target_norm - window_norm)
            
            if distance < 0.5: # آستانه شباهت
                c5 = prices[i+5]
                c6 = prices[i+6]
                change = ((c6 / c5) - 1) * 100
                found_matches.append({'change': change, 'bull': c6 > c5})

    if found_matches:
        total = len(found_matches)
        bulls = sum(1 for m in found_matches if m['bull'])
        bears = total - bulls
        avg_move = sum(m['change'] for m in found_matches) / total

        res = f"✅ **نتیجه تحلیل (V4):**\n\n"
        res += f"تعداد الگوهای مشابه یافت شده: `{total}`\n"
        res += f"رفتار کندل ۶ در تاریخچه:\n🟢 صعودی: {bulls} بار | 🔴 نزولی: {bears} بار\n\n"
        
        direction = "صعودی 📈" if avg_move > 0 else "نزولی 📉"
        res += f"🎯 **پیش‌بینی برای آینده (کندل ۰):**\n"
        res += f"احتمالاً حرکت **{direction}** خواهد بود.\n"
        res += f"میانگین شدت: `{avg_move:.2f}%`"
        
        await status_msg.edit_text(res, parse_mode='Markdown')
    else:
        await status_msg.edit_text("😔 الگوی مشابهی پیدا نشد.")

# مسیر سلامت برای Render
@app.get("/")
async def root():
    return {"status": "ok", "message": "Kamran Bot V4 is Running"}

# راه‌اندازی ربات در هنگام استارت آپ
@app.on_event("startup")
async def startup_event():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing!")
        return
        
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("سلام کامران عزیز! نام ارز را بفرست:")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_analysis))
    
    await application.initialize()
    await application.start()
    # استفاده از create_task برای جلوگیری از بلاک شدن سرور
    asyncio.create_task(application.updater.start_polling())
    logger.info("Bot started and polling...")

if __name__ == "__main__":
    # اجرای مستقیم uvicorn برای هماهنگی با پورت Render
    uvicorn.run(app, host="0.0.0.0", port=PORT)
