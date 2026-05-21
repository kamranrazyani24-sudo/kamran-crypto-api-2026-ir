import os
import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -------------------------
# /start command
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = (
        f"سلام {user.first_name} عزیز! 👋\n\n"
        "برای دریافت پیش‌بینی، نام ارز (مثلاً BTC) را بفرست.\n"
        "ربات تحلیل را انجام می‌دهد."
    )
    await update.message.reply_text(message)

# -------------------------
# Handle user message
# -------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    
    if not text:
        return

    # اضافه کردن USDT اگر لازم بود
    symbol = text if text.endswith("USDT") else f"{text}USDT"
    
    api_url = os.environ.get("FASTAPI_URL")
    if not api_url:
        await update.message.reply_text("خطای داخلی: آدرس API تنظیم نشده است.")
        return

    try:
        # فراخوانی API
        response = requests.get(f"{api_url}/predict/{symbol}", timeout=20)
        
        if response.status_code == 400:
            await update.message.reply_text("متأسفانه این نماد در لیست موجود نیست.")
            return
            
        data = response.json()
        if data.get("status") != "ok":
            await update.message.reply_text("خطا در پردازش تحلیل.")
            return

        if data.get("prediction") == "not_enough_matches":
            await update.message.reply_text(f"برای {symbol} الگوی مشابهی پیدا نشد.")
            return

        direction = "صعودی 📈" if data.get("direction") == "bullish" else "نزولی 📉"
        message = f"📊 پیش‌بینی برای {symbol}\n\nجهت احتمالی: {direction}\n\nموارد مشابه:"
        
        for m in data.get("matches", []):
            message += f"\n- {m['symbol']} (شباهت: {m['score']:.2f})"
        
        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("خطا در اتصال به سرور تحلیل.")

# -------------------------
# Run bot (Optimized for Threading)
# -------------------------
def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    # ایجاد یک event loop جدید برای جلوگیری از خطای Runtime
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Telegram bot is running...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
