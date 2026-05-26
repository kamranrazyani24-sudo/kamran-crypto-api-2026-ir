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

# تنظیمات لاگ برای عیب‌یابی
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

app = FastAPI()

# استخر ۳۰ ارز برتر برای پیدا کردن شباهت رفتار
SEARCH_POOL = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "DOGEUSDT", 
    "MATICUSDT", "LINKUSDT", "SHIBUSDT", "LTCUSDT", "TRXUSDT", "NEARUSDT", "ATOMUSDT", "UNIUSDT", 
    "XLMUSDT", "ETCUSDT", "FILUSDT", "LDOUSDT", "APTUSDT", "OPUSDT", "ARBUSDT", "TIAUSDT", "RNDRUSDT",
    "STXUSDT", "INJUSDT", "KASUSDT", "FETUSDT"
]

def fetch_data(symbol, limit=250):
    """دریافت داده از کوین‌اکس بدون تحریم"""
    try:
        url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=1hour&limit={limit}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                df = pd.DataFrame(data["data"], columns=['time', 'open', 'close', 'high', 'low', 'volume', 'amount'])
                return df.astype(float)
        return None
    except Exception:
        return None

def normalize(data):
    """نرمال‌سازی برای پیدا کردن شباهت در شکل موج (سینوسی یا U شکل)"""
    return (data - np.mean(data)) / (np.std(data) + 1e-9)

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.upper().replace("USDT", "")
    target_coin = user_input + "USDT"
    
    status_msg = await update.message.reply_text(f"🔍 کامران جان، در حال واکاوی الگو در ۳۰ ارز برتر برای {target_coin} هستم...")

    # ۱. استخراج الگوی ۹ کندل اخیر ارز هدف (کندل ۱ تا ۹)
    target_df = fetch_data(target_coin, limit=10)
    if target_df is None or len(target_df) < 10:
        await status_msg.edit_text("❌ خطا در دریافت داده‌های کوین‌اکس. نام ارز را درست وارد کردی؟")
        return

    # الگو شامل ۹ کندل بسته شده اخیر است
    target_pattern = target_df['close'].values[0:9] 
    target_norm = normalize(target_pattern)

    found_matches = []

    # ۲. جستجوی رفتار مشابه در تاریخچه ۳۰ ارز دیگر
    for symbol in SEARCH_POOL:
        source_df = fetch_data(symbol, limit=250)
        if source_df is None: continue
        
        source_prices = source_df['close'].values
        
        # بررسی پنجره‌ای (Windowing) برای پیدا کردن شباهت ۹ کندلی
        for i in range(len(source_prices) - 10):
            window = source_prices[i : i+9]
            window_norm = normalize(window)
            
            # محاسبه میزان شباهت (فاصله اقلیدسی)
            distance = np.linalg.norm(target_norm - window_norm)
            
            if distance < 0.45: # آستانه حساسیت به شباهت شکل
                # استخراج رفتار کندل شماره ۶ در آن الگوی خاص
                # (کندل ۶ نسبت به کندل ۵ قبل از خودش)
                c5 = source_prices[i+5]
                c6 = source_prices[i+6]
                change = ((c6 / c5) - 1) * 100
                
                found_matches.append({
                    'change': change,
                    'is_bullish': c6 > c5
                })

    # ۳. تحلیل نهایی بر اساس استراتژی کپی‌برداری کامران
    total = len(found_matches)
    if total > 0:
        bulls = sum(1 for m in found_matches if m['is_bullish'])
        bears = total - bulls
        avg_move = sum(m['change'] for m in found_matches) / total

        res = f"✅ تحلیل استراتژی V4 (مخصوص کامران):\n\n"
        res += f"تعداد الگوهای مشابه در ۳۰ ارز: {total} مورد\n"
        res += f"رفتار تاریخی کندل شماره ۶ در این الگوها:\n"
