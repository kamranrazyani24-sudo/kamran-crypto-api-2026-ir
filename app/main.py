import os
import asyncio
import uvicorn
from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ایمپورت کردن هندلرهایی که در فایل bot.py نوشتی
from app.bot import start, analyze
# ایمپورت کردن توکن از کانفیگ
from app.config import TELEGRAM_BOT_TOKEN

app = FastAPI(title="Crypto Pattern Bot")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot & Web Server are Running!"}

async def run_telegram_bot():
    # ساخت اپلیکیشن ربات
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # اضافه کردن هندلرهایی که در bot.py تعریف کردی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))

    # شروع به کار ربات
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # باز نگه داشتن تسک ربات
    while True:
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    # اجرای ربات بلافاصله بعد از بالا آمدن وب‌سرور
    asyncio.create_task(run_telegram_bot())

if __name__ == "__main__":
    # دریافت پورت از محیط Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
