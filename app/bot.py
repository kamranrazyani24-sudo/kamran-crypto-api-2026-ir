from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import (
    TELEGRAM_BOT_TOKEN,
    TOP_20_SYMBOLS,
    TIMEFRAMES,
    SIMILARITY_THRESHOLD,
    SCAN_LIMIT,
    MAX_MATCHES,
    MIN_CANDLES_REQUIRED
)
from data_fetcher import get_klines
from pattern import extract_pattern, _candle_features
from similarity import similarity


def get_candle_6_metrics(candle):
    o = float(candle[1])
    h = float(candle[2])
    l = float(candle[3])
    c = float(candle[4])

    body = abs(c - o)
    upper_shadow = h - max(o, c)
    lower_shadow = min(o, c) - l
    shadow = upper_shadow + lower_shadow
    rng = h - l
    range_pct = (rng / o) * 100 if o != 0 else 0.0

    return {
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "body": body,
        "shadow": shadow,
        "range": rng,
        "range_pct": range_pct,
    }


def build_window_pattern(candles_window):
    return extract_pattern(candles_window)


def analyze_symbol(symbol: str):
    """
    Target symbol analysis across all timeframes.
    Search in TOP_20_SYMBOLS x TIMEFRAMES.
    """
    results = []

    for tf in TIMEFRAMES:
        try:
            target_candles = get_klines(symbol, tf, limit=max(SCAN_LIMIT, MIN_CANDLES_REQUIRED))
            if len(target_candles) < MIN_CANDLES_REQUIRED:
                continue

            target_window = target_candles[-10:]
            target_pattern = build_window_pattern(target_window)

            for coin in TOP_20_SYMBOLS:
                try:
                    candles = get_klines(coin, tf, limit=SCAN_LIMIT)
                    if len(candles) < MIN_CANDLES_REQUIRED:
                        continue

                    for i in range(0, len(candles) - 9):
                        window = candles[i:i+10]
                        pattern = build_window_pattern(window)
                        score = similarity(target_pattern, pattern)

                        if score >= SIMILARITY_THRESHOLD:
                            c6_metrics = get_candle_6_metrics(window[5])
                            results.append({
                                "symbol": coin,
                                "timeframe": tf,
                                "score": score,
                                "metrics": c6_metrics
                            })

                except Exception:
                    continue

        except Exception:
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:MAX_MATCHES]

    if not top_results:
        return None

    avg_high = sum(x["metrics"]["high"] for x in top_results) / len(top_results)
    avg_low = sum(x["metrics"]["low"] for x in top_results) / len(top_results)
    avg_shadow = sum(x["metrics"]["shadow"] for x in top_results) / len(top_results)
    avg_body = sum(x["metrics"]["body"] for x in top_results) / len(top_results)
    avg_range_pct = sum(x["metrics"]["range_pct"] for x in top_results) / len(top_results)

    return {
        "matches": top_results,
        "average": {
            "high": avg_high,
            "low": avg_low,
            "shadow": avg_shadow,
            "body": avg_body,
            "range_pct": avg_range_pct
        }
    }


def format_report(symbol: str, analysis_result):
    if not analysis_result:
        return f"❌ برای {symbol} هیچ الگوی مشابهی پیدا نشد."

    lines = []
    lines.append(f"✅ تحلیل الگو برای {symbol}")
    lines.append("")
    lines.append("🔹 مشابهات برتر:")
    for i, item in enumerate(analysis_result["matches"], start=1):
        m = item["metrics"]
        lines.append(
            f"{i}) {item['symbol']} | {item['timeframe']} | Score: {item['score']:.4f}\n"
            f"   Candle 6 -> High: {m['high']:.8f} | Low: {m['low']:.8f}\n"
            f"   Body: {m['body']:.8f} | Shadow: {m['shadow']:.8f} | Range%: {m['range_pct']:.4f}%"
        )

    avg = analysis_result["average"]
    lines.append("")
    lines.append("📊 میانگین کندل ۶ در موارد مشابه:")
    lines.appen
