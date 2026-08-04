from core.state import ScoreComponents

STRENGTH_WEIGHTS = {"strong": 2.0, "moderate": 1.0, "weak": 0.5}


def compute_score(components: ScoreComponents) -> float:
    score = 0.0
    for factor in components.factors:
        weight = STRENGTH_WEIGHTS[factor.strength]
        score += weight if factor.supports_forecast else -weight
    return score


def score_to_label(score: float) -> str:
    if score >= 3:
        return "High"
    if score >= 1:
        return "Medium"
    return "Low"


def adjust_for_base_rate(computed_label: str, base_rate_pct: int) -> tuple[str, str]:
    label_to_range = {"Low": (0, 33), "Medium": (34, 66), "High": (67, 100)}
    lo, hi = label_to_range[computed_label]
    if lo <= base_rate_pct <= hi:
        return computed_label, "Consistent with historical base rate."
    note = (
        f"Evidence label ({computed_label}) diverges from base rate "
        f"({base_rate_pct}%). Treat as lower-confidence."
    )
    return computed_label, note