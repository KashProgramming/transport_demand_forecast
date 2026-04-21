"""Smoke tests for the FastAPI backend without external test dependencies."""
from __future__ import annotations

import asyncio
import json
import unittest

from backend.main import app


BASE_PAYLOAD = {
    "data_file": "data/yellow_tripdata_2025-01.csv",
    "use_sample": True,
    "sample_size": 1500,
}


async def _asgi_request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = b""
    headers: list[tuple[bytes, bytes]] = []

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers.append((b"content-type", b"application/json"))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": headers,
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }

    messages: list[dict] = []
    request_sent = False

    async def receive() -> dict:
        nonlocal request_sent
        if request_sent:
            return {"type": "http.disconnect"}
        request_sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict) -> None:
        messages.append(message)

    await app(scope, receive, send)

    status = next(
        message["status"] for message in messages if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"") for message in messages if message["type"] == "http.response.body"
    )
    parsed = json.loads(response_body.decode("utf-8")) if response_body else {}
    return status, parsed


class BackendSmokeTests(unittest.TestCase):
    """Endpoint-level smoke checks against the real ASGI app."""

    def test_health(self) -> None:
        status, payload = asyncio.run(_asgi_request("GET", "/health"))
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_non_model_endpoints(self) -> None:
        status, load_data = asyncio.run(_asgi_request("POST", "/api/load", BASE_PAYLOAD))
        self.assertEqual(status, 200)
        self.assertGreater(load_data["records_loaded"], 0)
        self.assertIn("summary_metrics", load_data)

        status, eda_data = asyncio.run(_asgi_request("POST", "/api/eda", BASE_PAYLOAD))
        self.assertEqual(status, 200)
        self.assertIn("figures", eda_data)
        self.assertIn("peak_hours", eda_data)

        status, spatial_data = asyncio.run(
            _asgi_request(
                "POST",
                "/api/spatial",
                {**BASE_PAYLOAD, "analyze_location": True},
            )
        )
        self.assertEqual(status, 200)
        self.assertIn("top_zones", spatial_data)
        self.assertIn("zone_statistics", spatial_data)

        status, data_info = asyncio.run(_asgi_request("POST", "/api/data-info", BASE_PAYLOAD))
        self.assertEqual(status, 200)
        self.assertIn("data_summary", data_info)
        self.assertIn("sample_data", data_info)


if __name__ == "__main__":
    unittest.main()
