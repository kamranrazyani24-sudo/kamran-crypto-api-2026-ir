
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
API_URL=os.getenv("FASTAPI_URL")

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! نماد ارز را بفرست مثل BTC یا ETH")

async def handle_symbol(update:Update, context:ContextTypes.DEFAULT_TYPE):
    symbol=update.message.text.upper().replace("USDT","")
    try:
        r=requests.get(f"{API_URL}/predict/{symbol}")
        data=r.json()
        await update.message.reply_text(str(data))
    except Exception as e:
        await update.message.reply_text("خطا در اتصال به سرور")

def run_bot():
    app=ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))
    print("Telegram bot is running...")
    app.run_polling()
