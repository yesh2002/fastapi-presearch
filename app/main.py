from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import httpx

from .config import settings
from .schemas import ImageUrlSearchRequest, SearchResponse, TextSearchRequest
from .upstream import UpstreamClient, normalize_results

app = FastAPI(title=settings.app_name, version="0.1.0")
upstream = UpstreamClient()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
async def search_image_upload(mode: str = settings.default_mode, image: UploadFile = File(...)) -> SearchResponse:
    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    try:
        raw = await upstream.image_search_bytes(image_bytes=contents, filename=image.filename or "upload.bin", mode=mode)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream network error: {exc}") from exc

    return SearchResponse(query=image.filename, mode=mode, items=normalize_results(raw), raw=raw)


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
