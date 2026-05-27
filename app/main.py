import os
import asyncio
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from app.bot import start, analyze
from app.config import BOT_TOKEN

# ۱. ساخت یک سرور وب بسیار ساده برای راضی نگه داشتن Render
app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "alive"}

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# ۲. تابع اصلی اجرای ربات
async def run_bot():
    print("🤖 Starting Telegram Bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze))
    
    # شروع به کار ربات
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # نگه داشتن ربات در حال اجرا
        await asyncio.Event().wait()

if __name__ == "__main__":
    # اجرای سرور وب در یک "رشته" (Thread) جداگانه
    # این باعث می‌شود پورت فوراً باز شود و Render ارور ندهد
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # اجرای ربات تلگرام در لاین اصلی
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
