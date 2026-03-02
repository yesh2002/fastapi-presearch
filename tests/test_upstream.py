from app.upstream import normalize_results


def test_normalize_results_supports_results_key():
    raw = {
        "results": [
            {
                "title": "A",
                "url": "https://a.example",
                "snippet": "sa",
                "thumbnail": "https://a.example/a.png",
            }
        ]
    }

    normalized = normalize_results(raw)

    assert normalized == [
        {
            "title": "A",
            "url": "https://a.example",
            "snippet": "sa",
            "thumbnail": "https://a.example/a.png",
            "raw": raw["results"][0],
        }
    ]


def test_normalize_results_supports_items_fallback_fields():
    raw = {
        "items": [
            {
                "name": "B",
                "link": "https://b.example",
                "description": "sb",
                "image": "https://b.example/b.png",
            }
        ]
    }

    normalized = normalize_results(raw)

    assert normalized[0]["title"] == "B"
    assert normalized[0]["url"] == "https://b.example"
    assert normalized[0]["snippet"] == "sb"
    assert normalized[0]["thumbnail"] == "https://b.example/b.png"


def test_normalize_results_supports_preview_key_and_thumb_field():
    raw = {
        "sid": "demo-sid",
        "preview": [
            {
                "name": "Model A",
                "username": "model_a",
                "thumb": "https://img.example/a.webp",
                "url": "https://explore.example/model_a",
            }
        ],
    }

    normalized = normalize_results(raw)

    assert len(normalized) == 1
    assert normalized[0]["title"] == "Model A"
    assert normalized[0]["url"] == "https://explore.example/model_a"
    assert normalized[0]["thumbnail"] == "https://img.example/a.webp"
    assert normalized[0]["raw"] == raw["preview"][0]
