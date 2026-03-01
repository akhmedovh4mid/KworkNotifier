"""
Kwork API client.

Provides async wrapper around Kwork internal endpoints
using curl_cffi with browser impersonation.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, NotRequired, TypedDict

from curl_cffi import AsyncSession
from curl_cffi.curl import CurlMime
from curl_cffi.requests.impersonate import BrowserTypeLiteral

logger = logging.getLogger(__name__)


class KworkAPIError(Exception):
    """Base exception for Kwork API errors."""


class CategoriesFilter(TypedDict):
    c: int
    attr: NotRequired[int]


class KworkAPI:
    """Async client for interacting with kwork.ru."""

    BASE_URL: str = "https://kwork.ru"

    def __init__(
        self,
        cookies: dict[str, str],
        impersonate: BrowserTypeLiteral = "firefox",
    ) -> None:
        """
        :param cookies: Authenticated session cookies.
        :param impersonate: Browser fingerprint type.
        """
        self.session = AsyncSession(
            cookies=cookies,
            impersonate=impersonate,
            timeout=15,
        )
        logger.debug("KworkAPI initialized with impersonate=%s", impersonate)

    def _headers(self, referer: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    async def _post_json(self, url: str, data: dict) -> dict:
        logger.debug("POST JSON → %s | payload=%s", url, data)

        resp = await self.session.post(url, json=data, headers=self._headers())
        resp.raise_for_status()

        if "application/json" not in resp.headers.get("Content-Type", ""):
            logger.error("Invalid response content-type: %s", resp.headers)
            raise KworkAPIError("Session invalid or blocked")

        return resp.json()

    async def _post_multipart(self, url: str, data: CurlMime) -> dict:
        logger.debug("POST MULTIPART → %s", url)

        resp = await self.session.post(
            url,
            multipart=data,
            headers=self._headers(),
        )
        resp.raise_for_status()

        if "application/json" not in resp.headers.get("Content-Type", ""):
            logger.error("Invalid response content-type: %s", resp.headers)
            raise KworkAPIError("Session invalid or blocked")

        return resp.json()

    def data_to_mime(self, data: list[tuple[str, Any]]) -> CurlMime:
        """Convert key-value pairs into CurlMime multipart payload."""
        mime = CurlMime()

        def _add_part(key: str, value: Any) -> None:
            if isinstance(value, list):
                for v in value:
                    _add_part(key, v)
            elif isinstance(value, dict):
                for subkey, subval in value.items():
                    _add_part(subkey, subval)
            elif isinstance(value, (int, str)):
                mime.addpart(name=key, data=str(value).encode())
            elif isinstance(value, bytes):
                mime.addpart(name=key, data=value)
            else:
                raise TypeError(f"Unsupported field type: {type(value)}")

        for k, v in data:
            _add_part(k, v)

        return mime

    async def get_projects(self, page: int, view: Literal[0, 1] | None = None) -> dict:
        """Fetch project list."""
        url = f"{self.BASE_URL}/projects"
        payload = [("page", page)]
        if view is not None:
            payload.append(("view", view))

        mime = self.data_to_mime(payload)
        result = await self._post_multipart(url, mime)

        logger.info("Fetched %s projects", len(result["data"]["wants"]))
        return result

    async def mark_viewed(self, want_ids: list[int]) -> dict:
        """Mark projects as viewed."""
        url = f"{self.BASE_URL}/api/offer/addview"
        logger.info("Marking viewed: %s", want_ids)
        return await self._post_json(url, {"wantIds": want_ids})

    async def __aenter__(self) -> "KworkAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()
        logger.debug("KworkAPI session closed")
