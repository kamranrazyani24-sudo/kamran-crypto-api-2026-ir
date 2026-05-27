from telegram import Update
from telegram.ext import ContextTypes
from app.data_fetcher import get_klines
from app.pattern import extract_pattern
from app.similarity import similarity
from app.config import SIMILARITY_THRESHOLD

import numpy as np


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام کامران عزیز 🌱\n"
        "اسم ارز رو بفرست (مثلاً BTC یا ADA)"
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    msg = await update.message.reply_text(f"⏳ در حال تحلیل {symbol} در تایم‌فریم ۱ ساعته...")

    closes = get_klines(symbol, timeframe="1h")
    if not closes or len(closes) < 20:
        await msg.edit_text("❌ داده کافی برای تحلیل وجود ندارد.")
        return

    target_pattern = extract_pattern(closes[-9:])

    matches_changes = []
    coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]

    for c in coins:
        data = get_klines(c, timeframe="1h")
        if not data or len(data) < 20:
            continue

        for i in range(len(data) - 10):
            window = data[i:i+10]
            pattern = extract_pattern(window[1:10])

            score = similarity(target_pattern, pattern)

            if score >= SIMILARITY_THRESHOLD:
                candle_5 = window[5]
                candle_6 = window[6]
                change = ((candle_6 - candle_5) / candle_5) * 100
                matches_changes.append(change)

    if matches_changes:
        avg_change = float(np.mean(matches_changes))
        direction = "📈 صعودی" if avg_change > 0 else "📉 نزولی"

        await msg.edit_text(
            f"✅ {len(matches_changes)} الگوی مشابه پیدا شد.\n"
            f"کندل ۰ ≈ کندل ۶\n"
            f"{direction}\n"
            f"میانگین تغییر: {avg_change:.2f}%"
        )
    else:
        await msg.edit_text("😔 الگوی مشابهی پیدا نشد.")
