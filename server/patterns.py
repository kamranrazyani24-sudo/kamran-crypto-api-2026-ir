import numpy as np

def extract_pattern(candles):
    closes = np.array([c["close"] for c in candles], dtype=float)
    highs = np.array([c["high"] for c in candles], dtype=float)
    lows = np.array([c["low"] for c in candles], dtype=float)
    volumes = np.array([c["volume"] for c in candles], dtype=float)

    closes_norm = (closes - closes.min()) / (closes.max() - closes.min() + 1e-9)
    slope = np.diff(closes_norm)
    curvature = np.diff(slope)

    center = len(closes_norm) // 2
    left_mean = closes_norm[:center].mean() if center > 0 else closes_norm.mean()
    right_mean = closes_norm[center:].mean() if center < len(closes_norm) else closes_norm.mean()
    mid = closes_norm[center] if len(closes_norm) > center else closes_norm.mean()
    u_shape_score = max(0.0, (left_mean + right_mean) / 2 - mid)

    t = np.linspace(0, np.pi, len(closes_norm))
    sine_pattern = np.sin(t)
    sine_score = float(np.corrcoef(closes_norm, sine_pattern)[0, 1]) if len(closes_norm) > 1 else 0.0
    if np.isnan(sine_score):
        sine_score = 0.0

    range_size = (highs - lows)
    body_size = np.abs(closes - np.array([c["open"] for c in candles], dtype=float))
    body_ratio = body_size / (range_size + 1e-9)

    fingerprint = np.concatenate([
        closes_norm,
        slope,
        curvature,
        [u_shape_score],
        [sine_score],
        volumes / (volumes.max() + 1e-9),
        body_ratio,
    ])
    return fingerprint
