from django.conf import settings
from elasticsearch import Elasticsearch

INDEX = "properties"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Elasticsearch(settings.ELASTICSEARCH_URL)
    return _client


def ensure_index():
    client = get_client()
    if client.indices.exists(index=INDEX):
        return
    client.indices.create(
        index=INDEX,
        mappings={
            "properties": {
                "title": {"type": "text", "fields": {"autocomplete": {"type": "search_as_you_type"}}},
                "description": {"type": "text"},
                "property_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "price": {"type": "float"},
                "bedrooms": {"type": "integer"},
                "bathrooms": {"type": "float"},
                "square_feet": {"type": "integer"},
                "city": {"type": "keyword"},
                "state": {"type": "keyword"},
                "postal_code": {"type": "keyword"},
                "country": {"type": "keyword"},
                "location": {"type": "geo_point"},
                "amenities": {"type": "keyword"},
                "images": {"type": "object", "enabled": False},
                "seller_id": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        },
    )


def to_doc(property_payload: dict) -> dict:
    doc = {
        "title": property_payload["title"],
        "description": property_payload.get("description", ""),
        "property_type": property_payload["property_type"],
        "status": property_payload["status"],
        "price": float(property_payload["price"]),
        "bedrooms": property_payload.get("bedrooms"),
        "bathrooms": float(property_payload.get("bathrooms") or 0),
        "square_feet": property_payload.get("square_feet"),
        "city": (property_payload.get("city") or "").lower(),
        "state": (property_payload.get("state") or "").lower(),
        "postal_code": property_payload.get("postal_code"),
        "country": property_payload.get("country"),
        "amenities": property_payload.get("amenities", []),
        "images": property_payload.get("images", []),
        "seller_id": property_payload.get("seller_id"),
        "created_at": property_payload.get("created_at"),
    }
    if property_payload.get("latitude") is not None and property_payload.get("longitude") is not None:
        doc["location"] = {"lat": property_payload["latitude"], "lon": property_payload["longitude"]}
    return doc


def index_property(property_payload: dict):
    ensure_index()
    if property_payload.get("status") != "active":
        remove_property(property_payload["id"])
        return
    get_client().index(index=INDEX, id=property_payload["id"], document=to_doc(property_payload), refresh=True)


def remove_property(property_id: str):
    try:
        get_client().delete(index=INDEX, id=property_id, refresh=True)
    except Exception:
        pass
