"""Tests for structured logging and compliance-gap risk flag."""
from __future__ import annotations

import logging

from trustagents.observability import get_logger, log_stage
from trustagents.oracle.models import FraudRiskBand, RetrievalStatus, SourceResult
from trustagents.oracle.stages.review import route_review
from trustagents.risk.core import generate_risk_flags


def test_get_logger_namespace():
    logger = get_logger("test.module")
    assert logger.name == "trustagents.test.module"


def test_log_stage_emits_start_and_complete(caplog):
    logger = get_logger("test.stages")
    with caplog.at_level(logging.INFO, logger="trustagents.test.stages"):
        with log_stage(logger, "test_stage", extra={"tenant_id": "t1"}):
            pass
    messages = [r.message for r in caplog.records]
    assert "stage_started" in messages
    assert "stage_completed" in messages


def test_log_stage_emits_error_on_exception(caplog):
    logger = get_logger("test.stages.err")
    with caplog.at_level(logging.ERROR, logger="trustagents.test.stages.err"):
        try:
            with log_stage(logger, "failing_stage"):
                raise RuntimeError("boom")
        except RuntimeError:
            pass
    assert any("stage_failed" in r.message for r in caplog.records)


def test_compliance_gap_flag_when_no_successful_source():
    sources = [
        SourceResult(
            source_id="s1",
            source_type="mock",
            query_performed={},
            retrieval_status=RetrievalStatus.NO_MATCH,
        )
    ]
    flags = generate_risk_flags([], sources)
    assert "compliance_gap" in flags


def test_no_compliance_gap_flag_when_source_succeeds():
    sources = [
        SourceResult(
            source_id="s1",
            source_type="mock",
            query_performed={},
            retrieval_status=RetrievalStatus.SUCCESS,
        )
    ]
    flags = generate_risk_flags([], sources)
    assert "compliance_gap" not in flags


def test_route_review_compliance_gap_reason_is_distinct():
    """compliance_gap risk flag must produce a distinct reason, not the generic coverage message."""
    _, _, needs_manual, reasons = route_review(
        band=FraudRiskBand.LOW,
        risk_flags=["compliance_gap"],
        policy_results=[],
        extraction_confidence=1.0,
        source_results_complete=False,
        conflicting_sources=False,
    )
    assert needs_manual is True
    assert any("Compliance gap" in r for r in reasons)
    assert not any(r == "Registry coverage incomplete" for r in reasons)


def test_route_review_incomplete_coverage_reason_without_compliance_gap():
    """Incomplete source coverage without the compliance_gap flag uses the generic message."""
    _, _, needs_manual, reasons = route_review(
        band=FraudRiskBand.LOW,
        risk_flags=[],
        policy_results=[],
        extraction_confidence=1.0,
        source_results_complete=False,
        conflicting_sources=False,
    )
    assert needs_manual is True
    assert any(r == "Registry coverage incomplete" for r in reasons)
    assert not any("Compliance gap" in r for r in reasons)
