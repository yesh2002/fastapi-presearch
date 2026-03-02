from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class TextSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    mode: str = Field(default="spicy")
    page: int = Field(default=1, ge=1)
    language: str | None = None


class ImageUrlSearchRequest(BaseModel):
    image_url: HttpUrl
    mode: str = Field(default="spicy")


class SearchResponse(BaseModel):
    query: str | None
    mode: str
    items: list[dict[str, Any]]
    raw: dict[str, Any]
