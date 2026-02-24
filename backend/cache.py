# cache.py
# Redis connection and caching utilities

import redis
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# REDIS CONNECTION
# ============================================

# Get Redis settings from environment
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# How long to keep URLs in cache (seconds)
# 3600 = 1 hour
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

# Create Redis client
# decode_responses=True means Redis returns
# strings instead of bytes
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True  # Return strings not bytes!
)

# ============================================
# TEST CONNECTION
# ============================================

def test_connection() -> bool:
    """
    Test if Redis is reachable.
    Returns True if connected, False if not.
    """
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False

# ============================================
# CACHE OPERATIONS
# ============================================

def cache_url(short_code: str, original_url: str) -> None:
    """
    Store a URL in Redis cache.

    Key format: "url:{short_code}"
    Example:    "url:google" → "https://google.com"

    Args:
        short_code:   The short code (e.g., "google")
        original_url: The original URL to cache
    """
    key = f"url:{short_code}"

    # setex = SET with EXpiry
    # After CACHE_TTL seconds, Redis deletes this automatically!
    redis_client.setex(
        name=key,           # The key
        time=CACHE_TTL,     # Expiry in seconds
        value=original_url  # The value
    )
    print(f"Cached: {key} → {original_url} (TTL: {CACHE_TTL}s)")


def get_cached_url(short_code: str):
    """
    Get a URL from Redis cache.

    Returns:
        The original URL string if found
        None if not in cache (cache miss)
    """
    key = f"url:{short_code}"
    cached = redis_client.get(key)

    if cached:
        print(f"Cache HIT: {key}")
        
    else:
        print(f"Cache MISS: {key}")

    return cached


def invalidate_url(short_code: str) -> None:
    """
    Remove a URL from cache.

    Used when URL is deleted or deactivated.
    We don't want old data served from cache!
    """
    key = f"url:{short_code}"
    redis_client.delete(key)
    print(f"Cache invalidated: {key}")


def get_cache_stats() -> dict:
    """
    Get Redis cache statistics.
    Useful for monitoring!
    """
    info = redis_client.info()
    return {
        "used_memory": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "total_keys": redis_client.dbsize(),
        "hits": info.get("keyspace_hits", 0),
        "misses": info.get("keyspace_misses", 0)
    }