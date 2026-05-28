from typing import List, Dict, Any


def extract_pattern(candles: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    طبق درخواست قبلی: فقط کندل‌های 7 تا 9 (ایندکس 6..8 اگر لیست 0-based باشد)
    اینجا اسکلت است تا importها درست باشند و بعداً منطق دقیق را جایگزین کنیم.
    """
    if len(candles) < 9:
        return {"ok": False, "reason": "not_enough_candles", "need": 9, "have": len(candles)}

    window = candles[6:9]  # candles 7..9
    return {"ok": True, "window": window}


def candle_features(candle: Dict[str, float]) -> Dict[str, float]:
    o = float(candle.get("open", 0))
    h = float(candle.get("high", 0))
    l = float(candle.get("low", 0))
    c = float(candle.get("close", 0))

    body = abs(c - o)
    upper_shadow = max(0.0, h - max(o, c))
    lower_shadow = max(0.0, min(o, c) - l)
    shadow = upper_shadow + lower_shadow

    return {
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "body": body,
        "upper_shadow": upper_shadow,
        "lower_shadow": lower_shadow,
        "shadow": shadow,
    }
