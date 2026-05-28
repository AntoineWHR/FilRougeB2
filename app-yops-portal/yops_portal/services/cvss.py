SEVERITY_THRESHOLDS = (
    (9.0, "critical"),
    (7.0, "high"),
    (4.0, "medium"),
    (0.0, "low"),
)


def severity_from_cvss(score: float) -> str:
    for threshold, label in SEVERITY_THRESHOLDS:
        if score >= threshold:
            return label
    return "low"


def parse_cvss(raw: str) -> float:
    score = float(raw)
    if not 0.0 <= score <= 10.0:
        raise ValueError("CVSS hors plage 0-10")
    return round(score, 1)
