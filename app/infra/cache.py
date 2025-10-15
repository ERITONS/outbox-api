import json
import redis
from core.config import Settings

_redis = redis.from_url(Settings().REDIS_URL, decode_responses=True)

def chache_get(key: str):
    val = _redis.get(key)
    if val:
        return json.loads(val) 
    return None

def cache_set(key: str, value: dict, ttl_seconds: int = 60):
    _redis.setex(key, ttl_seconds,json.dumps(value))

def cache_del(key: str):
    _redis.delete(key)