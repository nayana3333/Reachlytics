from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.models.agent_decision import AgentDecision
from app.models.graph_edge import GraphEdge
from app.models.persona import Persona
from app.models.simulation import Simulation, SimulationRound
from app.models.video import Video
from app.services.agent_reason_service import enrich_decision_reasons_with_source
from app.services.ai_analysis_service import analyze_content
from app.services.persona_service import generate_personas_with_source
from app.services.report_service import create_report
from app.services.transcript_service import create_transcript
from app.ml.verdict_classifier import predict_pre_sim_verdict
from app.simulation.propagation import run_propagation

logger = logging.getLogger(__name__)


def _set_progress(db: Session, simulation: Simulation, stage: str, status: str = "processing") -> None:
    simulation.status = status
    simulation.progress_stage = stage
    simulation.error_message = None
    db.commit()


def execute_simulation(db: Session, simulation_id: str) -> Simulation:
    simulation = db.get(Simulation, simulation_id)
    if not simulation:
        raise ValueError("Simulation not found")

    try:
        _set_progress(db, simulation, "starting")

        video = db.get(Video, simulation.video_id)
        _set_progress(db, simulation, "transcribing")
        transcript = video.transcript or create_transcript(db, video)
        _set_progress(db, simulation, "analyzing_content")
        analysis = video.content_analysis or analyze_content(
            db, video.id, transcript.text, simulation.target_audience, video.file_path
        )

        analysis_dict = {
            "hook_score": analysis.hook_score,
            "clarity_score": analysis.clarity_score,
            "emotional_appeal_score": analysis.emotional_appeal_score,
            "shareability_score": analysis.shareability_score,
            "audience_fit_score": analysis.audience_fit_score,
        }
        _set_progress(db, simulation, "generating_personas")
        persona_dicts, personas_ai_source = generate_personas_with_source(
            simulation.persona_count, simulation.target_audience
        )
        simulation.personas_ai_source = personas_ai_source
        db.commit()
        in_target_percentage = sum(1 for persona in persona_dicts if persona["in_target"]) / max(1, len(persona_dicts))
        ml_verdict_prediction = predict_pre_sim_verdict(
            {
                **analysis_dict,
                "population_size": simulation.persona_count,
                "in_target_percentage": in_target_percentage,
            }
        )
        _set_progress(db, simulation, "simulating_spread")
        result = run_propagation(
            persona_dicts, analysis_dict, simulation.target_audience, simulation.round_count
        )
        _set_progress(db, simulation, "generating_reasons")
        result["decisions"], reasons_ai_source = enrich_decision_reasons_with_source(
            result["decisions"],
            result["personas"],
            transcript.text,
            {
                **analysis_dict,
                "product_category": analysis.product_category,
                "summary": analysis.summary,
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
            },
            simulation.target_audience,
        )
        simulation.reasons_ai_source = reasons_ai_source
        db.commit()

        persona_rows: list[Persona] = []
        for persona in result["personas"]:
            row = Persona(simulation_id=simulation.id, **persona)
            db.add(row)
            persona_rows.append(row)
        db.flush()

        for decision in result["decisions"]:
            persona = persona_rows[decision["persona_index"]]
            db.add(
                AgentDecision(
                    simulation_id=simulation.id,
                    persona_id=persona.id,
                    round_number=decision["round_number"],
                    watched=decision["watched"],
                    liked=decision["liked"],
                    commented=decision["commented"],
                    shared=decision["shared"],
                    engagement_score=decision["engagement_score"],
                    reason=decision["reason"],
                )
            )

        for edge in result["edges"]:
            db.add(
                GraphEdge(
                    simulation_id=simulation.id,
                    source_persona_id=persona_rows[edge["source"]].id,
                    target_persona_id=persona_rows[edge["target"]].id,
                    weight=edge["weight"],
                    relationship_type=edge["type"],
                )
            )

        for round_data in result["rounds"]:
            db.add(SimulationRound(simulation_id=simulation.id, **round_data))

        _set_progress(db, simulation, "saving_results")
        metrics = result["metrics"]
        simulation.virality_score = metrics["virality_score"]
        simulation.predicted_reach = metrics["predicted_reach"]
        simulation.like_rate = metrics["like_rate"]
        simulation.comment_rate = metrics["comment_rate"]
        simulation.share_rate = metrics["share_rate"]
        simulation.cascade_depth = metrics["cascade_depth"]
        simulation.final_verdict = metrics["verdict"]
        db.commit()

        _set_progress(db, simulation, "generating_report")
        try:
            create_report(db, simulation.id, metrics, ml_verdict_prediction)
        except Exception as exc:
            logger.exception("Report creation failed for simulation %s", simulation.id)
            raise RuntimeError(f"Report creation failed: {exc}") from exc

        simulation.status = "completed"
        simulation.progress_stage = "completed"
        simulation.completed_at = datetime.utcnow()
        simulation.error_message = None
        db.commit()
        db.refresh(simulation)
        return simulation
    except Exception as exc:
        logger.exception("Simulation failed: %s", simulation_id)
        db.rollback()
        simulation = db.get(Simulation, simulation_id)
        if simulation:
            simulation.status = "failed"
            simulation.progress_stage = "failed"
            simulation.error_message = str(exc)[:1000]
            db.commit()
            db.refresh(simulation)
            return simulation
        raise
