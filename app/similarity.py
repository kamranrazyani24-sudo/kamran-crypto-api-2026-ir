import math

def _cosine_similarity(a, b):
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)

def _distance_score(a, b):
    """
    Convert average absolute distance to a [0,1] score.
    Lower distance => higher score.
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")

    avg_dist = sum(abs(x - y) for x, y in zip(a, b)) / len(a)
    return 1 / (1 + avg_dist)

def similarity(a, b):
    """
    Hybrid score:
    65% cosine similarity
    35% distance-based similarity
    """
    cos = _cosine_similarity(a, b)
    dist = _distance_score(a, b)
    score = (0.65 * cos) + (0.35 * dist)
    return max(0.0, min(1.0, score))
