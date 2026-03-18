"""Pydantic models for GitHub App webhook payload schema validation."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class GitHubRepository(BaseModel):
    id: int
    full_name: str
    private: bool = False


class GitHubSender(BaseModel):
    id: int
    login: str
    type: str = "User"


class GitHubInstallation(BaseModel):
    id: int
    account: dict[str, Any] = Field(default_factory=dict)


class GitHubCheckSuite(BaseModel):
    id: int
    head_sha: str
    head_branch: str | None = None
    status: str | None = None
    conclusion: str | None = None


class GitHubCheckRun(BaseModel):
    id: int
    name: str
    head_sha: str
    status: str | None = None
    conclusion: str | None = None


class PullRequestRef(BaseModel):
    number: int
    head: dict[str, Any] = Field(default_factory=dict)
    base: dict[str, Any] = Field(default_factory=dict)


class WebhookPayload(BaseModel):
    """Top-level GitHub webhook payload with required envelope fields."""

    action: str | None = None
    installation: GitHubInstallation | None = None
    repository: GitHubRepository | None = None
    sender: GitHubSender | None = None

    # Event-specific optional sections
    check_suite: GitHubCheckSuite | None = None
    check_run: GitHubCheckRun | None = None
    pull_request: PullRequestRef | None = None

    @model_validator(mode="before")
    @classmethod
    def require_sender_or_installation(cls, values: dict[str, Any]) -> dict[str, Any]:
        """At least one of sender or installation must be present for meaningful routing."""
        if not values.get("sender") and not values.get("installation"):
            raise ValueError("Payload must contain at least one of 'sender' or 'installation'")
        return values


class CheckRunOutput(BaseModel):
    """Output section for a GitHub check run."""

    title: str = Field(max_length=255)
    summary: str = Field(max_length=65535)
    text: str | None = Field(default=None, max_length=65535)


class CreateCheckRunRequest(BaseModel):
    """Request body for creating or updating a GitHub check run."""

    owner: str
    repo: str
    name: str = Field(max_length=255)
    head_sha: str = Field(min_length=40, max_length=40)
    status: str = Field(pattern="^(queued|in_progress|completed)$")
    conclusion: str | None = Field(
        default=None,
        pattern="^(success|failure|neutral|cancelled|skipped|timed_out|action_required)$",
    )
    output: CheckRunOutput | None = None
    external_id: str | None = Field(default=None, max_length=255)
