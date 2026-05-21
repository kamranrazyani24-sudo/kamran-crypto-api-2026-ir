import os
import asyncio
from fastapi import FastAPI, Request
from bots.telegram_bot import process_update

app = FastAPI()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    # ربات را بدون ترد و پروسه اجرا می‌کنیم
    await process_update(update, TOKEN)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
