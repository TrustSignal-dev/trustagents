from pydantic import BaseModel


class FeatureFlags(BaseModel):
    oracle_api_enabled: bool = True
    async_jobs_enabled: bool = False
    http_connectors_enabled: bool = False
    experimental_risk_heuristics_enabled: bool = True
    trustsignal_handoff_export_enabled: bool = False
    github_app_webhook_enabled: bool = False


class Settings(BaseModel):
    feature_flags: FeatureFlags = FeatureFlags()
    required_sources: tuple[str, ...] = ("mock_registry",)


settings = Settings()
