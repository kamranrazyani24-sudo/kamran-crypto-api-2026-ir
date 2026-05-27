import os
import asyncio
import uvicorn
from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ایمپورت هندلرها از فایل bot
from app.bot import start, analyze
# ایمپورت ایمن کانفیگ
try:
    from app.config import TELEGRAM_BOT_TOKEN
except ImportError:
    # اگر در کانفیگ نام دیگری دارد، اینجا دستی ست کن یا ارور را مدیریت کن
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_FALLBACK_TOKEN")

app = FastAPI(title="Crypto Pattern Bot")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Server is up!"}

async def run_telegram_bot():
    if not TELEGRAM_BOT_TOKEN or "YOUR" in TELEGRAM_BOT_TOKEN:
        print("❌ Error: Telegram Token not found in config.py")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_bot())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
