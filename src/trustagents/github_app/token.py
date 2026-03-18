"""GitHub App installation token lifecycle with least-privilege usage.

Token management constraints
-----------------------------
- Tokens are fetched on-demand and **never cached** between requests.
- The token is used once, then discarded; callers must not store it.
- Token requests use only the installation ID supplied by the verified webhook
  payload — no user-supplied IDs are accepted.
- GitHub installation tokens expire after 1 hour.  Since we never cache them
  this is not a concern in practice, but callers should be aware.

Configuration (environment variables)
--------------------------------------
GITHUB_APP_ID          — numeric GitHub App ID (required for production)
GITHUB_APP_PRIVATE_KEY — PEM-encoded private key (required for production)

In the current simulation scope these are optional; if absent, token
acquisition returns a sentinel string so that integration tests can run
without real credentials.
"""
from __future__ import annotations

import os
import time

from trustagents.observability import get_logger

logger = get_logger("github_app.token")

# Sentinel used in tests / simulation mode when real credentials are absent.
_SIMULATION_TOKEN = "ghs_simulation_token_not_for_production"


def _app_credentials_configured() -> bool:
    return bool(os.environ.get("GITHUB_APP_ID") and os.environ.get("GITHUB_APP_PRIVATE_KEY"))


def get_installation_token(installation_id: int) -> str:
    """Return a short-lived installation access token for the given installation.

    In production this must generate a JWT-signed request to the GitHub API
    and exchange it for an installation token.  In simulation/test mode (no
    credentials configured) it returns a sentinel string and logs a warning.

    Args:
        installation_id: The GitHub App installation ID from the webhook payload.

    Returns:
        A bearer token string valid for at most one request.

    Raises:
        RuntimeError: If credential configuration is detected but token
            acquisition fails.  Callers should surface this as a 500.
    """
    if not _app_credentials_configured():
        logger.warning(
            "installation_token_simulation_mode",
            extra={
                "installation_id": installation_id,
                "note": "GITHUB_APP_ID / GITHUB_APP_PRIVATE_KEY not configured; using sentinel",
            },
        )
        return _SIMULATION_TOKEN

    # Production path: generate a JWT and exchange it for an installation token.
    # This stub raises NotImplementedError so that accidental production use
    # without wiring up the real credential flow fails loudly.
    raise NotImplementedError(
        "Real installation-token acquisition is not yet implemented. "
        "Set GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY and provide a concrete "
        "implementation before deploying to production."
    )


def discard_token(token: str) -> None:
    """Symbolic discard to document that tokens must not be retained past the request.

    If a revocation API is wired in the future, this is the integration point.
    Note: Python strings are immutable; this function cannot overwrite the
    caller's reference, but it marks the intended token lifetime boundary.
    """
    logger.debug("installation_token_discarded", extra={"ts": time.monotonic()})
