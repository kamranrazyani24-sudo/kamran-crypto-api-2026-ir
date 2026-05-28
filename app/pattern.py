def _candle_features(candle):
    """
    Convert one candle to normalized features.
    candle format:
    [open_time, open, high, low, close, volume, ...]
    """
    o = float(candle[1])
    h = float(candle[2])
    l = float(candle[3])
    c = float(candle[4])

    if o == 0:
        o = 1e-12

    body = (c - o) / o
    upper_shadow = (h - max(o, c)) / o
    lower_shadow = (min(o, c) - l) / o
    range_pct = (h - l) / o

    return [body, upper_shadow, lower_shadow, range_pct]

def extract_pattern(candles):
    """
    Extract pattern only from candles 7 to 9.
    candles must contain at least 9 candles.
    Python indices:
    candle 7 -> index 6
    candle 8 -> index 7
    candle 9 -> index 8
    """
    if len(candles) < 9:
        raise ValueError("At least 9 candles required for pattern extraction")

    segment = candles[6:9]
    pattern = []
    for candle in segment:
        pattern.extend(_candle_features(candle))
    return pattern
