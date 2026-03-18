"""Tests for structured logging and compliance-gap risk flag."""
from __future__ import annotations

import logging

from trustagents.observability import get_logger, log_stage
from trustagents.oracle.models import RetrievalStatus, SourceResult
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
