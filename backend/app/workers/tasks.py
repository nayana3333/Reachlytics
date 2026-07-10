import logging

from app.db.database import SessionLocal
from app.models.simulation import Simulation
from app.services.simulation_service import execute_simulation
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="run_simulation")
def run_simulation_task(simulation_id: str) -> str:
    db = SessionLocal()
    try:
        execute_simulation(db, simulation_id)
        return simulation_id
    except Exception:
        logger.exception("Simulation failed: %s", simulation_id)
        simulation = db.get(Simulation, simulation_id)
        if simulation:
            simulation.status = "failed"
            simulation.progress_stage = "failed"
            simulation.error_message = "Simulation worker failed. Check backend logs for details."
            db.commit()
        raise
    finally:
        db.close()
