import httpx

from trustagents.connectors.file_source import fetch as file_fetch
from trustagents.connectors.http_json import fetch as http_fetch
from trustagents.oracle.models import RetrievalStatus


def test_file_source_retrieval_shape():
    result, payload = file_fetch({"identifier": "ID-12345"}, "tests/fixtures/source_records.json")
    assert result.retrieval_status == RetrievalStatus.SUCCESS
    assert payload["fullName"] == "Alex Carter"


def test_http_json_connector_mocked_response(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"fullName": "Alex Carter", "sourceFreshness": "stale"}

    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: DummyResponse())
    result, payload = http_fetch({"identifier": "ID-12345"}, "https://synthetic.test")
    assert result.retrieval_status == RetrievalStatus.SUCCESS
    assert result.source_freshness == "stale"
    assert payload["fullName"] == "Alex Carter"
