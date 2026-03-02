from __future__ import annotations

from typing import Any

import httpx

from .config import settings


class UpstreamClient:
    def __init__(self) -> None:
        self.timeout = settings.upstream_timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": settings.upstream_user_agent,
        }
        if settings.upstream_authorization:
            headers["Authorization"] = settings.upstream_authorization
        if settings.upstream_cookie:
            headers["Cookie"] = settings.upstream_cookie
        if settings.upstream_origin:
            headers["Origin"] = settings.upstream_origin
        if settings.upstream_referer:
            headers["Referer"] = settings.upstream_referer
        return headers

    async def text_search(self, *, query: str, mode: str, page: int, language: str | None) -> dict[str, Any]:
        payload = {
            "q": query,
            "mode": mode,
            "page": page,
        }
        if language:
            payload["language"] = language

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(settings.upstream_text_url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def image_search_bytes(
        self,
        *,
        image_bytes: bytes,
        filename: str,
        mode: str,
        limit_preview: int | None = None,
    ) -> dict[str, Any]:
        files = {
            "image": (filename, image_bytes, "application/octet-stream"),
        }
        data = {"mode": mode}
        if limit_preview is not None:
            data["limit_preview"] = str(limit_preview)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(settings.upstream_image_url, data=data, files=files, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def image_search_results(self, *, sid: str, limit: int, offset: int) -> dict[str, Any]:
        params = {"sid": sid, "limit": limit, "offset": offset}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(settings.upstream_image_url, params=params, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def image_search_url(self, *, image_url: str, mode: str) -> dict[str, Any]:
        payload = {"image_url": image_url, "mode": mode}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(settings.upstream_image_url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()


def normalize_results(raw: dict[str, Any]) -> list[dict[str, Any]]:
    source_items = raw.get("results") or raw.get("items") or raw.get("preview") or []
    normalized: list[dict[str, Any]] = []
    for item in source_items:
        normalized.append(
            {
                "title": item.get("title") or item.get("name"),
                "url": item.get("url") or item.get("link"),
                "snippet": item.get("snippet") or item.get("description"),
                "thumbnail": item.get("thumbnail") or item.get("image") or item.get("thumb"),
                "raw": item,
            }
        )
    return normalized
