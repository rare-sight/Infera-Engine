from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field


class Scenario(BaseModel):
    name: str = Field(description="Short scenario name")
    description: str = Field(description="4-6 sentence narrative")
    probability: str = Field(description="High / Medium / Low")
    probability_reason: str = Field(description="Short justification for the probability")
    key_drivers: List[str] = Field(description="Main forces driving this future")
    early_signals: List[str] = Field(description="Observable indicators that this scenario is emerging")


class ScenarioSet(BaseModel):
    scenarios: List[Scenario]


class InferaState(TypedDict):
    topic: str
    analysis: str
    research: str
    uncertainties: str
    scenarios_text: str
    structured_scenarios: Optional[dict]
    current_step: str