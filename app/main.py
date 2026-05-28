from fastapi import FastAPI
from app.bot import start_bot # فرض بر اینکه در bot.py یک تابع start داری

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # اینجا می‌توانی bot را استارت کنی
    print("Bot is starting...")

@app.get("/")
def read_root():
    return {"status": "Service is running"}
