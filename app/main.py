import os
import asyncio
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from app.bot import start, analyze
from app.config import BOT_TOKEN

app = FastAPI()

@app.get("/")
def health():
    return {"status": "up"}

def run_web():
    # این تابع پورت را سریعاً برای رندر باز می‌کند
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

async def run_bot():
    # صبر کوچک برای اطمینان از بالا آمدن وب‌سرور
    await asyncio.sleep(2)
    print("🤖 Starting Bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze))
    
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    # اجرای وب‌سرور در ترد جداگانه
    threading.Thread(target=run_web, daemon=True).start()
    # اجرای ربات در ترد اصلی
    asyncio.run(run_bot())
