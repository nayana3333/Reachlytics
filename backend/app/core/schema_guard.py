from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
from sqlalchemy.engine import Engine


REQUIRED_COLUMNS = {
    "simulations": {
        "id",
        "status",
        "progress_stage",
        "error_message",
        "personas_ai_source",
        "reasons_ai_source",
        "virality_score",
        "predicted_reach",
        "final_verdict",
    },
    "transcripts": {"id", "video_id", "text", "confidence", "ai_source"},
    "content_analyses": {"id", "video_id", "summary", "visual_description", "ai_source"},
    "personas": {"id", "simulation_id", "name", "engagement_tendency"},
    "agent_decisions": {"id", "simulation_id", "persona_id", "reason"},
    "graph_edges": {"id", "simulation_id", "source_persona_id", "target_persona_id"},
    "simulation_rounds": {"id", "simulation_id", "round_number"},
    "reports": {"id", "simulation_id", "summary", "ml_verdict_prediction"},
}


def assert_schema_current(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    missing_tables = sorted(set(REQUIRED_COLUMNS) - tables)
    if missing_tables:
        raise RuntimeError(
            "Database schema is missing required tables "
            f"{missing_tables}. Run `alembic upgrade head` from backend/ before starting the API."
        )

    missing_columns: dict[str, list[str]] = {}
    for table, required_columns in REQUIRED_COLUMNS.items():
        columns = {column["name"] for column in inspector.get_columns(table)}
        missing = sorted(required_columns - columns)
        if missing:
            missing_columns[table] = missing

    if missing_columns:
        raise RuntimeError(
            "Database schema is out of date. Missing columns: "
            f"{missing_columns}. Run `alembic upgrade head` from backend/ before starting the API."
        )


def assert_alembic_head(engine: Engine) -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    script = ScriptDirectory.from_config(alembic_cfg)
    expected_head = script.get_current_head()

    with engine.connect() as connection:
        current_revision = MigrationContext.configure(connection).get_current_revision()

    if current_revision != expected_head:
        raise RuntimeError(
            "Database migration revision is out of date. "
            f"Current revision: {current_revision or 'none'}; expected head: {expected_head}. "
            "Run `alembic upgrade head` from backend/ before starting the API or worker."
        )
