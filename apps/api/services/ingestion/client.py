"""
Thin HTTP client for the football-data.org v4 API.

Free tier: 10 requests/minute → enforce a 6.5 s inter-request delay.
On 429, wait for the reset window indicated by the response header, then retry once.
"""

import time
from typing import Any, Optional

import httpx

BASE_URL = "https://api.football-data.org/v4"
_DEFAULT_DELAY = 6.5  # seconds between requests (free tier: 10 req/min)


class FootballDataClient:
    def __init__(self, api_key: str, request_delay: float = _DEFAULT_DELAY) -> None:
        self._client = httpx.Client(
            headers={"X-Auth-Token": api_key},
            timeout=30.0,
        )
        self._delay = request_delay
        self._last_request_time: float = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        wait = self._delay - elapsed
        if wait > 0:
            time.sleep(wait)

    def get(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        self._throttle()
        resp = self._client.get(f"{BASE_URL}{path}", params=params)
        self._last_request_time = time.monotonic()

        if resp.status_code == 429:
            reset_in = int(resp.headers.get("X-RequestCounter-Reset", 60))
            time.sleep(reset_in)
            return self.get(path, params)

        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FootballDataClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
