import numpy as np

def extract_pattern(closes):
    closes = np.array(closes, dtype=float)

    norm = (closes - closes.mean()) / (closes.std() + 1e-9)
    slope = np.diff(norm)
    curvature = np.diff(slope)

    fingerprint = np.concatenate([norm, slope, curvature])
    return fingerprint
