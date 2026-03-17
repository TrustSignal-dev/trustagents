from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from trustagents.oracle.models import JobResponse, OracleDecision


@dataclass
class JobRecord:
    status: str
    result: OracleDecision | None = None
    error: str | None = None


class InMemoryJobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, JobRecord] = {}

    def create(self) -> str:
        job_id = str(uuid4())
        self.jobs[job_id] = JobRecord(status="queued")
        return job_id

    def set_running(self, job_id: str) -> None:
        self.jobs[job_id].status = "running"

    def set_completed(self, job_id: str, result: OracleDecision) -> None:
        self.jobs[job_id].status = "completed"
        self.jobs[job_id].result = result

    def set_failed(self, job_id: str, error: str) -> None:
        self.jobs[job_id].status = "failed"
        self.jobs[job_id].error = error

    def get(self, job_id: str) -> JobResponse | None:
        record = self.jobs.get(job_id)
        if not record:
            return None
        return JobResponse(job_id=job_id, status=record.status, result=record.result, error=record.error)


job_store = InMemoryJobStore()
