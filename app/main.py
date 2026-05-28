import os
from fastapi import FastAPI
from bot import analyze_symbol # این خط در لاگ تو خطا می‌داد

app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "Bot is running..."}

@app.get("/predict/{symbol}")
async def predict(symbol: str):
    # فراخوانی تابع تحلیل از bot.py
    results = await analyze_symbol(symbol.upper())
    return results

if __name__ == "__main__":
    import uvicorn
    # رندر پورت را از Environment Variable می‌خواند
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
