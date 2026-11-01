from typing import Literal

from pydantic import BaseModel, model_validator


class EvidenceRecord(BaseModel):
    claim: str

    evidence_label: Literal[
        "VERIFIED",
        "REPORTED",
        "HYPOTHESIS",
    ]

    supporting_evidence: str

    source_name: str | None = None
    source_url: str | None = None

    source_type: Literal[
        "PRIMARY",
        "SECONDARY",
        "INFERENCE",
    ]

    confidence: Literal[
        "HIGH",
        "MEDIUM",
        "LOW",
    ]
 

    @model_validator(mode="after")
    def validate_evidence_semantics(self):
        if self.source_type == "INFERENCE" and self.evidence_label != "HYPOTHESIS":
            raise ValueError(
                "Evidence with source_type='INFERENCE' must use "
                "evidence_label='HYPOTHESIS'."
            )

        if self.evidence_label in {"VERIFIED", "REPORTED"} and not self.source_url:
            raise ValueError(
                "Evidence labeled VERIFIED or REPORTED must include a source_url."
            )

        return self


class LeadResearchReport(BaseModel):
    company_overview: str
    business_model: str
    market_position: str

    key_decision_makers: list[str]
    recent_developments: list[str]

    potential_business_needs: list[str]

    evidence: list[EvidenceRecord]



class EvaluationScore(BaseModel):
    score: Literal[1, 2, 3, 4, 5]
    reasoning: str
    findings: list[str]


class JudgeEvaluationReport(BaseModel):
    evidence_grounding: EvaluationScore
    evidence_classification: EvaluationScore
    solution_grounding: EvaluationScore
    decision_quality: EvaluationScore
    actionability: EvaluationScore

    overall_assessment: str
    key_strengths: list[str]
    key_weaknesses: list[str]
    recommended_improvements: list[str]


class HumanReviewRecord(BaseModel):
    run_id: str
    company_name: str
    reviewer: str | None = None
    status: Literal[
        "PENDING",
        "APPROVED",
        "REJECTED",
        "REVISION_REQUESTED",
    ] = "PENDING"
    review_comment: str | None = None
    reviewed_at: str | None = None



class CRMLead(BaseModel):
    lead_id: str
    company_name: str
    run_id: str

    status: Literal[
        "NEW",
        "QUALIFIED",
        "DISQUALIFIED",
        "CONTACTED",
    ] = "NEW"

    next_action: str | None = None
    updated_at: str | None = None
