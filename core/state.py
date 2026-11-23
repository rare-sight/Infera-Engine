from typing import Literal, TypedDict

from pydantic import AliasChoices, BaseModel, Field, model_validator


class EntityCard(BaseModel):
    name: str
    entity_type: Literal["person", "organization", "policy", "event", "product", "other"] = Field(
        validation_alias=AliasChoices("entity_type", "type")
    )
    jurisdiction: str
    role_or_context: str = Field(
        validation_alias=AliasChoices("role_or_context", "role")
    )
    disambiguation_note: str = Field(
        default="",
        validation_alias=AliasChoices("disambiguation_note", "note"),
    )
    resolution_stage: Literal["provisional", "reconciled"] = "provisional"

    @model_validator(mode="before")
    @classmethod
    def normalize_field_names(cls, value):
        if not isinstance(value, dict):
            return value

        aliases = {
            "name": "name",
            "entity_type": "entity_type",
            "type": "entity_type",
            "jurisdiction": "jurisdiction",
            "role_or_context": "role_or_context",
            "role": "role_or_context",
            "disambiguation_note": "disambiguation_note",
            "note": "disambiguation_note",
            "resolution_stage": "resolution_stage",
        }
        return {
            canonical_key: field_value
            for key, field_value in value.items()
            if (canonical_key := aliases.get(str(key).strip().lower()))
        }


class EvidenceFactor(BaseModel):
    factor: str
    supports_forecast: bool  # True if makes THIS scenario's claim more likely
    strength: Literal["strong", "moderate", "weak"]
    reason: str


class ScoreComponents(BaseModel):
    factors: list[EvidenceFactor] = Field(min_length=3, max_length=6)


class Scenario(BaseModel):
    scenario_name: str
    time_horizon: Literal["3-6mo", "6-12mo", "1-3yr"]
    forecast_statement: str
    inferred_from: list[str]
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    score_components: ScoreComponents
    @model_validator(mode="before")
    @classmethod
    def normalize_evidence(cls, value):
        if not isinstance(value, dict):
            return value

        value = value.copy()
        evidence = value.pop("evidence", None)
        if evidence is not None and "score_components" not in value:
            value["score_components"] = {"factors": evidence}

        score_components = value.get("score_components")
        if isinstance(score_components, ScoreComponents):
            factors = score_components.factors
        elif isinstance(score_components, dict):
            factors = score_components.get("factors", [])
        else:
            factors = []
        if factors:
            if "evidence_for" not in value:
                value["evidence_for"] = [
                    factor.factor if isinstance(factor, EvidenceFactor) else factor["factor"]
                    for factor in factors
                    if (
                        isinstance(factor, EvidenceFactor)
                        and factor.supports_forecast is True
                    )
                    or (
                        isinstance(factor, dict)
                        and factor.get("supports_forecast") is True
                        and isinstance(factor.get("factor"), str)
                    )
                ][:3]
            if "evidence_against" not in value:
                value["evidence_against"] = [
                    factor.factor if isinstance(factor, EvidenceFactor) else factor["factor"]
                    for factor in factors
                    if (
                        isinstance(factor, EvidenceFactor)
                        and factor.supports_forecast is False
                    )
                    or (
                        isinstance(factor, dict)
                        and factor.get("supports_forecast") is False
                        and isinstance(factor.get("factor"), str)
                    )
                ][:3]
        return value


class ScenarioSet(BaseModel):
    scenarios: list[Scenario] = Field(
        min_length=3,
        max_length=3,
        validation_alias=AliasChoices("scenarios", "scenario_set"),
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_scenarios(cls, value):
        if isinstance(value, dict):
            for key, scenarios in value.items():
                if str(key).strip().lower() in {"scenarios", "scenario_set"}:
                    return {"scenarios": scenarios}
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    normalized = cls.normalize_scenarios(item)
                    if normalized is not item:
                        return normalized
        return value


class BaseRateEstimate(BaseModel):
    reference_class: str
    estimated_base_rate_pct: int = Field(ge=0, le=100)
    base_rate_reasoning: str
    comparable_cases: list[str] = []


class InferaState(TypedDict):
    topic: str
    entity_card: dict | None
    base_rate: dict | None
    analysis: str
    research: str
    uncertainties: str
    scenarios_text: str
    structured_scenarios: dict | None
    current_step: str
