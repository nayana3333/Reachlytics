from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, simulations, videos
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.queue_status import queue_backend
from app.core.schema_guard import assert_alembic_head, assert_schema_current
from app.db.database import Base, engine
from app.ml.verdict_classifier import warm_verdict_model
import app.models  # noqa: F401

settings = get_settings()
configure_logging()

is_memory_sqlite = settings.normalized_database_url == "sqlite:///:memory:"

if is_memory_sqlite:
    Base.metadata.create_all(bind=engine)
else:
    assert_alembic_head(engine)

assert_schema_current(engine)
warm_verdict_model()

app = FastAPI(
    title=settings.app_name,
    description="AI-assisted agent simulation platform for product demo virality prediction.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")


@app.get("/health", tags=["health"])
def health():
    backend = queue_backend()
    return {
        "status": "ok",
        "service": "reachlytics",
        "queue_backend": backend,
        "queue_label": "Celery" if backend == "celery" else "Inline (Redis unavailable)",
    }
