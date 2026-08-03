from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field


class Scenario(BaseModel):
    name: str = Field(description="Short evocative scenario name")
    description: str = Field(description="4-6 concrete sentences")
    probability: str = Field(description="High / Medium / Low")
    probability_reason: str = Field(description="One short sentence justifying the probability")
    key_drivers: List[str] = Field(description="3-5 main drivers")
    early_signals: List[str] = Field(description="3-4 observable early signals")


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