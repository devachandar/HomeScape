"""
Cross-service event bus (Redis Pub/Sub) - matches the original Node.js
HomeScape design. Every service that changes something another service
cares about publishes a small JSON event here instead of calling the
other service's API directly. Interested services run a `listen_events`
management command (see listen_events.py) that subscribes to the
channels it cares about and reacts independently.
"""
import json
from datetime import datetime, timezone

import redis
from django.conf import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.REDIS_URL)
    return _client


def publish_event(event_name: str, payload: dict):
    message = json.dumps(
        {
            "event": event_name,
            "payload": payload,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        },
        default=str,
    )
    try:
        _get_client().publish(event_name, message)
    except redis.RedisError as exc:
        import logging

        logging.getLogger(__name__).warning("Could not publish %s: %s", event_name, exc)
