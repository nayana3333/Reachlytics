import redis

from app.core.config import get_settings


def redis_available() -> bool:
    settings = get_settings()
    client = None
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=0.5, socket_timeout=0.5)
        return bool(client.ping())
    except Exception:
        return False
    finally:
        if client is not None:
            client.close()


def queue_backend() -> str:
    return "celery" if redis_available() else "inline"
