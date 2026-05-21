import numpy as np

def similarity(pattern_a, pattern_b):
    a = np.asarray(pattern_a, dtype=float).flatten()
    b = np.asarray(pattern_b, dtype=float).flatten()

    min_len = min(len(a), len(b))
    if min_len == 0:
        return 0.0
    a = a[:min_len]
    b = b[:min_len]

    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    cos = float(np.dot(a, b) / denom)
    point_score = float(np.exp(-np.mean(np.abs(a - b))))
    final = (0.65 * cos) + (0.35 * point_score)
    return float(final)
