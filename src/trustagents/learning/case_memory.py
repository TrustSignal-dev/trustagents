from __future__ import annotations

from dataclasses import dataclass, field

from trustagents.oracle.models import ReviewedCaseInput, ReviewedCaseRecord, ReviewerFeedbackInput, SimilarCaseReference


@dataclass
class CaseMemoryStore:
    _cases: list[ReviewedCaseRecord] = field(default_factory=list)

    def add_case(self, data: ReviewedCaseInput) -> ReviewedCaseRecord:
        case = ReviewedCaseRecord(case_id=f"case-{len(self._cases) + 1:05d}", **data.model_dump())
        self._cases.append(case)
        return case

    def apply_feedback(self, feedback: ReviewerFeedbackInput) -> ReviewedCaseRecord | None:
        for case in self._cases:
            if case.case_id == feedback.case_id:
                case.reviewer_disposition = feedback.reviewer_disposition
                case.false_positive = feedback.false_positive
                case.false_negative = feedback.false_negative
                return case
        return None

    def similar_cases(self, feature_digest: str, limit: int = 3) -> list[SimilarCaseReference]:
        ranked: list[SimilarCaseReference] = []
        for case in self._cases:
            score = _similarity(feature_digest, case.feature_digest)
            if score <= 0:
                continue
            ranked.append(
                SimilarCaseReference(
                    case_id=case.case_id,
                    similarity_score=score,
                    outcome=case.outcome,
                    reviewer_disposition=case.reviewer_disposition,
                )
            )
        ranked.sort(key=lambda item: item.similarity_score, reverse=True)
        return ranked[:limit]


def _similarity(one: str, two: str) -> float:
    if not one or not two:
        return 0.0
    if one == two:
        return 1.0
    one_parts = set(one.split("|"))
    two_parts = set(two.split("|"))
    union = one_parts | two_parts
    if not union:
        return 0.0
    return round(len(one_parts & two_parts) / len(union), 4)


case_memory_store = CaseMemoryStore()
