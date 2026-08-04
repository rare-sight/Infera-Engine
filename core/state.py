from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field


class EntityCard(BaseModel):
    name: str
    entity_type: Literal["person", "organization", "policy", "event", "product", "other"]
    jurisdiction: str
    role_or_context: str
    disambiguation_note: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"
    resolution_stage: Literal["provisional", "reconciled"] = "provisional"


class EvidenceFactor(BaseModel):
    factor: str
    supports_forecast: bool  # True if makes THIS scenario's claim more likely
    strength: Literal["strong", "moderate", "weak"]
    reason: str


class ScoreComponents(BaseModel):
    factors: List[EvidenceFactor] = Field(min_length=3, max_length=6)


class Scenario(BaseModel):
    scenario_name: str
    time_horizon: Literal["3-6mo", "6-12mo", "1-3yr"]
    forecast_statement: str
    inferred_from: List[str]
    evidence_for: List[str]
    evidence_against: List[str]
    score_components: ScoreComponents
    score: float = 0.0
    probability_label: Literal["Low", "Medium", "High"] = "Low"
    probability_reason: str = ""


class ScenarioSet(BaseModel):
    scenarios: List[Scenario]


class BaseRateEstimate(BaseModel):
    reference_class: str
    estimated_base_rate_pct: int = Field(ge=0, le=100)
    base_rate_reasoning: str
    comparable_cases: List[str] = []


class InferaState(TypedDict):
    topic: str
    entity_card: Optional[dict]
    base_rate: Optional[dict]
    analysis: str
    research: str
    uncertainties: str
    scenarios_text: str
    structured_scenarios: Optional[dict]
    current_step: str