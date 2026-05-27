import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from app.bot import start, analyze
from app.config import BOT_TOKEN

app = FastAPI()

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    await telegram_app.start()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "running", "TF": "1h"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
