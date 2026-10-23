"""Cliente Redis: caché semántica (RNF-01), inactividad de sesión (RNF-03), idempotencia."""

from redis.asyncio import Redis, from_url

from app.config import settings

redis: Redis = from_url(settings.REDIS_URL, decode_responses=True)
