from fastapi import FastAPI, HTTPException

from bot import analyze_symbol, format_report

app = FastAPI(title="Crypto Pattern Bot")


@app.get("/")
def root():
    return {"status": "ok", "message": "Crypto Pattern Bot is running"}


@app.get("/predict/{symbol}")
def predict(symbol: str):
    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol = f"{symbol}USDT"

    try:
        result = analyze_symbol(symbol)
        if not result:
            raise HTTPException(status_code=404, detail="No similar pattern found")

        return {
            "symbol": symbol,
            "analysis": result,
            "report": format_report(symbol, result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
