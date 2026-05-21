import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! نام ارز دیجیتال را بفرست (مثلاً BTC)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.upper()
    await update.message.reply_text(f"در حال تحلیل {symbol}...")
    # اینجا درخواست به API اصلی ات را اضافه می‌کنی

async def run_bot():
    if not TOKEN:
        print("خطا: توکن تلگرام تنظیم نشده است!")
        return
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(">>> ربات تلگرام با موفقیت اجرا شد")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
