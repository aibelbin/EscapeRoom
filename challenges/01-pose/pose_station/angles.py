import math


def angle_deg(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> float:
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    na = math.hypot(*ba)
    nc = math.hypot(*bc)
    if na == 0 or nc == 0:
        return 0.0
    cosine = max(-1.0, min(1.0, (ba[0] * bc[0] + ba[1] * bc[1]) / (na * nc)))
    return math.degrees(math.acos(cosine))
