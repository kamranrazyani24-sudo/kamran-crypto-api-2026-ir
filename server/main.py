from fastapi import FastAPI, HTTPException
from .data_fetcher import get_klines
from .patterns import extract_pattern
from .similarity import similarity
from . import config

app = FastAPI(title="Crypto Pattern Bot")

MARKET = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT",
    "DOTUSDT","TRXUSDT","AVAXUSDT","ATOMUSDT","LINKUSDT","LTCUSDT",
]

@app.get("/")
def root():
    return {"status": "ok", "message": "Crypto Pattern Bot is running"}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    try:
        target_candles = get_klines(symbol, config.TIMEFRAME, 9)
        target_pattern = extract_pattern(target_candles)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch target symbol: {e}")

    matches = []
    for s in MARKET:
        if s == symbol:
            continue
        try:
            candles = get_klines(s, config.TIMEFRAME, 9)
            pattern = extract_pattern(candles)
            score = similarity(target_pattern, pattern)
            if score >= config.SIMILARITY_THRESHOLD:
                matches.append({"symbol": s, "score": round(score, 4)})
        except Exception:
            continue

    matches.sort(key=lambda x: x["score"], reverse=True)
    matches = matches[:config.MAX_MATCH]

    if len(matches) < config.MIN_MATCH:
        return {
            "status": "not_enough_matches",
            "message": "کمتر از 10 ارز مشابه یافت شد",
            "symbol": symbol,
            "total_matches": len(matches),
            "matches": matches,
        }

    c6 = target_candles[-3]
    prediction = {
        "direction": "bullish" if c6["close"] > c6["open"] else "bearish",
        "candle_6": c6,
    }

    return {
        "status": "ok",
        "symbol": symbol,
        "total_matches": len(matches),
        "matches": matches,
        "prediction": prediction,
    }
