from __future__ import annotations

import time
from typing import Any

from trustagents.observability import get_logger

logger = get_logger("connectors.retry")

_DEFAULT_MAX_RETRIES = 2
_DEFAULT_BASE_DELAY = 0.5


def with_retry(
    fn: Any,
    *args: Any,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    base_delay: float = _DEFAULT_BASE_DELAY,
    retryable_exceptions: tuple[type[BaseException], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """Call *fn* with positional and keyword args, retrying on transient failures.

    Uses exponential back-off: ``base_delay * 2 ** attempt`` seconds between retries.
    Only exceptions listed in *retryable_exceptions* trigger a retry; all others
    propagate immediately.
    """
    last_exc: BaseException | None = None
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except retryable_exceptions as exc:
            last_exc = exc
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "retry_scheduled",
                    extra={"attempt": attempt + 1, "max_retries": max_retries, "delay_s": delay},
                )
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]
