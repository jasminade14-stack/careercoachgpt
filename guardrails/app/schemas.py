from pydantic import BaseModel, Field
from typing import List, Optional

class Recommendation(BaseModel):
    title: str = Field(..., min_length=2)
    match_score: float = Field(..., ge=0.0, le=1.0)
    why: str = Field(..., min_length=10)

class BiasAudit(BaseModel):
    risk_level: str = Field(..., description="low|medium|high")
    notes: str = Field(..., min_length=5)

class CareerCoachOutput(BaseModel):
    recommendations: List[Recommendation]
    bias_audit: BiasAudit
    sources_used: Optional[List[str]] = []
