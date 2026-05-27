import asyncio
import os
import uvicorn
from fastapi import FastAPI
from app.bot import main as run_bot

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running..."}

async def start_services():
    # اجرای ربات تلگرام در پس‌زمینه
    asyncio.create_task(run_bot())
    
    # تنظیم پورت برای Render
    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_services())
