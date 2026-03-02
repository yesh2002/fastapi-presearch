from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import httpx

from .config import settings
from .schemas import ImageUrlSearchRequest, SearchResponse, TextSearchRequest
from .upstream import UpstreamClient, normalize_results

app = FastAPI(title=settings.app_name, version="0.1.0")
upstream = UpstreamClient()
UI_FILE_PATH = Path(__file__).resolve().parent / "static" / "neon-search.html"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ui", include_in_schema=False)
async def neon_ui() -> FileResponse:
    if not UI_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="UI file not found")
    return FileResponse(UI_FILE_PATH)


@app.post("/api/search/text", response_model=SearchResponse)
async def search_text(payload: TextSearchRequest) -> SearchResponse:
    try:
        raw = await upstream.text_search(
            query=payload.query,
            mode=payload.mode or settings.default_mode,
            page=payload.page,
            language=payload.language,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream network error: {exc}") from exc

    return SearchResponse(
        query=payload.query,
        mode=payload.mode,
        items=normalize_results(raw),
        raw=raw,
    )


@app.post("/api/search/image/upload", response_model=SearchResponse)
async def search_image_upload(
    mode: str = settings.default_mode,
    fetch_full: bool = Query(default=False),
    full_limit: int = Query(default=40, ge=1, le=80),
    image: UploadFile = File(...),
) -> SearchResponse:
    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    try:
        raw = await upstream.image_search_bytes(
            image_bytes=contents,
            filename=image.filename or "upload.bin",
            mode=mode,
        )
        if fetch_full and raw.get("sid"):
            raw = await upstream.image_search_results(sid=str(raw["sid"]), limit=full_limit, offset=0)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream network error: {exc}") from exc

    return SearchResponse(query=image.filename, mode=mode, items=normalize_results(raw), raw=raw)


@app.get("/api/search/image/results")
async def search_image_results(
    sid: str,
    limit: int = Query(default=40, ge=1, le=80),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    try:
        raw = await upstream.image_search_results(sid=sid, limit=limit, offset=offset)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream network error: {exc}") from exc

    return {
        "sid": raw.get("sid") or sid,
        "items": normalize_results(raw),
        "has_more": bool(raw.get("hasMore")),
        "next_offset": int(raw.get("nextOffset") or 0),
        "total": raw.get("total"),
        "raw": raw,
    }


@app.post("/api/search/image/url", response_model=SearchResponse)
async def search_image_url(payload: ImageUrlSearchRequest) -> SearchResponse:
    try:
        raw = await upstream.image_search_url(image_url=str(payload.image_url), mode=payload.mode)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream network error: {exc}") from exc

    return SearchResponse(query=str(payload.image_url), mode=payload.mode, items=normalize_results(raw), raw=raw)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Unexpected server error: {exc}"})
