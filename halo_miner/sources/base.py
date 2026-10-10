from __future__ import annotations

import logging
import time
from typing import Any, Dict, Iterable, List, Optional

import requests

from ..models import Post

log = logging.getLogger("halo_miner")

USER_AGENT = "halo-miner/0.1 (voice-of-customer research for https://studioquattrodesign.com)"


class SourceError(RuntimeError):
    pass


class HttpClient:
    """Small polite HTTP wrapper: fixed delay, retries with backoff, one UA."""

    def __init__(self, delay: float = 1.2, retries: int = 3, timeout: float = 30.0, session: Optional[requests.Session] = None):
        self.delay, self.retries, self.timeout = delay, retries, timeout
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", USER_AGENT)
        self._last = 0.0

    def _throttle(self) -> None:
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def request(self, method: str, url: str, **kw: Any) -> requests.Response:
        kw.setdefault("timeout", self.timeout)
        err: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            self._throttle()
            try:
                resp = self.session.request(method, url, **kw)
            except requests.RequestException as e:  # network layer
                err = e
            else:
                if resp.status_code == 429 or resp.status_code >= 500:
                    retry_after = float(resp.headers.get("Retry-After", 0) or 0)
                    err = SourceError(f"{resp.status_code} from {url}")
                    time.sleep(max(retry_after, 2.0 * (2 ** attempt)))
                    continue
                return resp
            time.sleep(2.0 * (2 ** attempt))
        raise SourceError(f"request failed after {self.retries + 1} attempts: {url}: {err}")

    def get_json(self, url: str, **kw: Any) -> Any:
        resp = self.request("GET", url, **kw)
        if resp.status_code >= 400:
            raise SourceError(f"{resp.status_code} from {url}: {resp.text[:200]}")
        return resp.json()

    def get_text(self, url: str, **kw: Any) -> str:
        resp = self.request("GET", url, **kw)
        if resp.status_code >= 400:
            raise SourceError(f"{resp.status_code} from {url}")
        return resp.text


class BaseSource:
    name = "base"

    def __init__(self, http: Optional[HttpClient] = None):
        self.http = http or HttpClient()

    def fetch(self, config: Dict[str, Any]) -> List[Post]:  # pragma: no cover - interface
        raise NotImplementedError


def dedupe(posts: Iterable[Post]) -> List[Post]:
    seen = set()
    out: List[Post] = []
    for p in posts:
        key = (p.source, p.url or p.id, p.text[:160].lower())
        if key in seen or not p.text:
            continue
        seen.add(key)
        out.append(p)
    return out
