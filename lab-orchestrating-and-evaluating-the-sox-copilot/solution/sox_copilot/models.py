# sox_copilot/models.py

# [TEACHING POINT] Pydantic = our "contract gate".
# We validate the final payloads at graph boundaries for auditability.

from typing import List
from pydantic import BaseModel, Field

class Population(BaseModel):
    tested_count: int = Field(ge=0)
    criteria: str

class EvidencePayload(BaseModel):
    control_id: str
    period: str
    violations_found: int = Field(ge=0)
    violation_entries: List[str]
    policy_summary: str
    population: Population
    narrative: str

class ReviewPayload(BaseModel):
    reviewed_control_id: str
    period: str
    evidence_valid: bool
    issues: List[str]
    review_notes: str
