import os
import logging
import requests

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
        f"سلام {user.first_name} 👋\n\n"
        "نماد ارز را ارسال کن.\n"
        "مثال:\n"
        "BTC\n"
        "ETH\n"
        "BIT\n\n"
        "ربات الگوهای مشابه را در بازار Binance بررسی می‌کند."
    )

    await update.message.reply_text(message)


# -------------------------
# Handle user message
# -------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip().upper()

    if not text:
        await update.message.reply_text("نماد معتبر ارسال کن.")
        return

    # اگر USDT نداشت اضافه کن
    if not text.endswith("USDT"):
        symbol = f"{text}USDT"
    else:
        symbol = text

    logger.info(f"User requested symbol: {symbol}")

    api_url = os.environ.get("FASTAPI_URL")

    if not api_url:
        await update.message.reply_text("خطای تنظیمات سرور.")
        logger.error("FASTAPI_URL not set")
        return

    url = f"{api_url}/predict/{symbol}"

    try:

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":
            await update.message.reply_text("خطا در دریافت داده.")
            return

        if data.get("prediction") == "not_enough_matches":
            await update.message.reply_text(
                f"برای {symbol} الگوی مشابه کافی پیدا نشد ❌"
            )
            return

        direction = data.get("direction")
        matches = data.get("matches", [])

        if direction == "bullish":
            direction_text = "صعودی 📈"
        else:
            direction_text = "نزولی 📉"

        message = f"پیش‌بینی برای {symbol}\n\n"
        message += f"جهت احتمالی: {direction_text}\n\n"
        message += "ارزهای با الگوی مشابه:\n"

        if matches:
            for m in matches:
                s = m.get("symbol", "N/A")
                score = m.get("score", 0)
                message += f"{s} | score: {score:.3f}\n"
        else:
            message += "مورد مشابهی پیدا نشد."

        await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        await update.message.reply_text("خطا در اتصال به سرور.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("خطا در پردازش درخواست.")


# -------------------------
# Run bot
# -------------------------
def run_bot():

    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Telegram bot started")

    app.run_polling()


# -------------------------
# Local test
# -------------------------
if __name__ == "__main__":
    run_bot()
