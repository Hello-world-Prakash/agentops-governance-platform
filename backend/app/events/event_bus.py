import asyncio
import json
from typing import Any, AsyncIterator, Dict

from app.config import REDIS_URL

TRACE_CHANNEL_PREFIX = "trace:"
_memory_events: dict[str, list[dict[str, Any]]] = {}


def _channel(trace_id: str) -> str:
    return f"{TRACE_CHANNEL_PREFIX}{trace_id}"


def publish_trace_event(trace_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    event = {"trace_id": trace_id, "event_type": event_type, "payload": payload}
    _memory_events.setdefault(trace_id, []).append(event)

    if not REDIS_URL:
        return

    try:
        import redis

        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        client.publish(_channel(trace_id), json.dumps(event, default=str))
    except Exception:
        return


async def stream_trace_events(trace_id: str) -> AsyncIterator[dict[str, Any]]:
    for event in _memory_events.get(trace_id, []):
        yield event

    if not REDIS_URL:
        return

    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        pubsub = client.pubsub()
        await pubsub.subscribe(_channel(trace_id))
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                yield json.loads(message["data"])
        finally:
            await pubsub.unsubscribe(_channel(trace_id))
            await pubsub.close()
            await client.aclose()
    except Exception:
        await asyncio.sleep(0)
        return
