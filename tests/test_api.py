from fastapi.testclient import TestClient

from app.main import app


class FakeUpstream:
    async def text_search(self, *, query: str, mode: str, page: int, language: str | None):
        return {
            "results": [
                {
                    "title": f"{query}-result",
                    "url": "https://example.com",
                    "snippet": "demo",
                }
            ]
        }

    async def image_search_bytes(self, *, image_bytes: bytes, filename: str, mode: str):
        return {"results": [{"name": filename, "link": "https://img.example.com"}]}

    async def image_search_url(self, *, image_url: str, mode: str):
        return {"items": [{"title": image_url, "url": "https://img.example.com/item"}]}


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_text_search_endpoint(monkeypatch):
    from app import main as main_module

    monkeypatch.setattr(main_module, "upstream", FakeUpstream())

    response = client.post(
        "/api/search/text",
        json={"query": "fastapi", "mode": "spicy", "page": 1},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "fastapi"
    assert data["mode"] == "spicy"
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "fastapi-result"


def test_image_upload_endpoint(monkeypatch):
    from app import main as main_module

    monkeypatch.setattr(main_module, "upstream", FakeUpstream())

    response = client.post(
        "/api/search/image/upload?mode=spicy",
        files={"image": ("photo.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "photo.jpg"
    assert data["items"][0]["title"] == "photo.jpg"


def test_image_url_endpoint(monkeypatch):
    from app import main as main_module

    monkeypatch.setattr(main_module, "upstream", FakeUpstream())

    response = client.post(
        "/api/search/image/url",
        json={"image_url": "https://cdn.example.com/a.jpg", "mode": "spicy"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "https://cdn.example.com/a.jpg"
    assert data["items"][0]["url"] == "https://img.example.com/item"
