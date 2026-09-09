from core.scoring import adjust_for_base_rate, compute_score, score_to_label
from core.state import EvidenceFactor, ScoreComponents


def test_compute_score_uses_factor_direction_and_strength() -> None:
    components = ScoreComponents(
        factors=[
            EvidenceFactor(
                factor="Strong support", supports_forecast=True, strength="strong", reason="test"
            ),
            EvidenceFactor(
                factor="Weak opposition", supports_forecast=False, strength="weak", reason="test"
            ),
            EvidenceFactor(
                factor="Moderate support",
                supports_forecast=True,
                strength="moderate",
                reason="test",
            ),
        ]
    )
    assert compute_score(components) == 2.5


def test_score_to_label_boundaries() -> None:
    assert score_to_label(3) == "High"
    assert score_to_label(1) == "Medium"
    assert score_to_label(0.99) == "Low"


def test_base_rate_adjustment_flags_divergence() -> None:
    label, note = adjust_for_base_rate("High", 20)
    assert label == "High"
    assert "diverges" in note
