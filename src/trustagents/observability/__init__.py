from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator


def get_logger(name: str) -> logging.Logger:
    """Return a logger scoped to the trustagents namespace."""
    return logging.getLogger(f"trustagents.{name}")


@contextmanager
def log_stage(
    logger: logging.Logger, stage: str, *, extra: dict[str, Any] | None = None
) -> Generator[dict[str, Any], None, None]:
    """Context manager that logs entry/exit for a pipeline stage with duration."""
    context: dict[str, Any] = extra.copy() if extra else {}
    context["stage"] = stage
    logger.info("stage_started", extra=context)
    start = time.monotonic()
    try:
        yield context
    except Exception:
        elapsed = round((time.monotonic() - start) * 1000, 2)
        context["duration_ms"] = elapsed
        logger.error("stage_failed", extra=context, exc_info=True)
        raise
    else:
        elapsed = round((time.monotonic() - start) * 1000, 2)
        context["duration_ms"] = elapsed
        logger.info("stage_completed", extra=context)
