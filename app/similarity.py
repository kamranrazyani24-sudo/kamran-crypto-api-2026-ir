import numpy as np

def similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    L = min(len(a), len(b))
    if L == 0:
        return 0.0

    a = a[:L]
    b = b[:L]

    cos = float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))
    point_score = float(np.exp(-np.mean(np.abs(a - b))))

    return 0.65 * cos + 0.35 * point_score
