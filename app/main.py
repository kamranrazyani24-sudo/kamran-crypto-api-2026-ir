from fastapi import FastAPI, Query
from app.bot import start, analyze

app = FastAPI(title="Crypto Pattern Bot", version="1.0.0")


@app.get("/")
def root():
    return {"status": "ok", "service": "crypto-pattern-bot"}


@app.get("/start")
def start_endpoint():
    return start()


@app.get("/analyze")
def analyze_endpoint(
    symbol: str = Query(default="ADA", description="Symbol like ADA, BTC, ETH"),
):
    return analyze(symbol)
