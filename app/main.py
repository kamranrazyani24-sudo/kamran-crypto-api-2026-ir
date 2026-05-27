import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from app.bot import start, analyze
from app.config import BOT_TOKEN

app = FastAPI()

# تعریف اپلیکیشن تلگرام در سطح ماژول
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

@app.on_event("startup")
async def startup():
    # اضافه کردن هندلرها
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze))
    
    # مقداردهی اولیه
    await telegram_app.initialize()
    await telegram_app.start()
    
    # اجرای پولینگ به صورت غیرمسدودکننده (Background Task)
    # این کار باعث می‌شود سرور فست‌اپی بلافاصله پورت را باز کند و رندر خطا ندهد
    asyncio.create_task(telegram_app.updater.start_polling())
    print("✅ Telegram Bot (Polling) started in background.")

@app.get("/")
async def root():
    return {"status": "running", "user": "Kamran", "mode": "Polling"}

if __name__ == "__main__":
    # دریافت پورت از رندر
    port = int(os.environ.get("PORT", 10000))
    # اجرای سرور وب
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
