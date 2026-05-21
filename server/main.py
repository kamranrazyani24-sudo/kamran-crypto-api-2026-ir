
import threading
from fastapi import FastAPI
from bots.telegram_bot import run_bot

app=FastAPI(title="Crypto Pattern Bot")

MARKET=["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT"]

@app.get("/")
def root():
    return {"status":"running"}

@app.get("/predict/{symbol}")
def predict(symbol:str):
    s=symbol.upper().replace("USDT","")+"USDT"
    if s not in MARKET:
        return {"error":"symbol not supported"}
    return {
        "symbol":s,
        "prediction":"sample signal",
        "confidence":0.63
    }


def start_bot():
    run_bot()

bot_thread=threading.Thread(target=start_bot,daemon=True)
bot_thread.start()
