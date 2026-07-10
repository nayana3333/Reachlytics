from fastapi import APIRouter, Depends, HTTPException
import networkx as nx
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.queue_status import redis_available
from app.db.database import get_db
from app.models.agent_decision import AgentDecision
from app.models.graph_edge import GraphEdge
from app.models.persona import Persona
from app.models.report import Report
from app.models.simulation import Simulation, SimulationRound
from app.models.user import User
from app.models.video import Video
from app.schemas.simulation import (
    GraphEdgeResponse,
    GraphNode,
    SimulationCreate,
    SimulationGraphResponse,
    SimulationResponse,
)
from app.services.simulation_service import execute_simulation
from app.workers.tasks import run_simulation_task

router = APIRouter(prefix="/simulations", tags=["simulations"])


def _attach_ai_sources(simulation: Simulation) -> Simulation:
    simulation.transcript_ai_source = (
        simulation.video.transcript.ai_source if simulation.video and simulation.video.transcript else "fallback"
    )
    simulation.content_analysis_ai_source = (
        simulation.video.content_analysis.ai_source
        if simulation.video and simulation.video.content_analysis
        else "fallback"
    )
    return simulation


@router.post("", response_model=SimulationResponse, status_code=201)
def create_simulation(
    payload: SimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = db.query(Video).filter(Video.id == payload.video_id, Video.user_id == current_user.id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    simulation = Simulation(user_id=current_user.id, **payload.model_dump())
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    if redis_available():
        try:
            run_simulation_task.delay(simulation.id)
        except Exception:
            # Developer fallback: run inline when Redis/Celery is not available.
            execute_simulation(db, simulation.id)
    else:
        execute_simulation(db, simulation.id)
    db.refresh(simulation)
    return _attach_ai_sources(simulation)


@router.get("", response_model=list[SimulationResponse])
def list_simulations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulations = (
        db.query(Simulation)
        .filter(Simulation.user_id == current_user.id)
        .order_by(Simulation.created_at.desc())
        .all()
    )
    return [_attach_ai_sources(simulation) for simulation in simulations]


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    simulation = (
        db.query(Simulation)
        .filter(Simulation.id == simulation_id, Simulation.user_id == current_user.id)
        .first()
    )
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _attach_ai_sources(simulation)


@router.get("/{simulation_id}/status")
def get_status(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    return {
        "id": simulation.id,
        "status": simulation.status,
        "progress_stage": simulation.progress_stage,
        "error_message": simulation.error_message,
        "transcript_ai_source": simulation.transcript_ai_source,
        "content_analysis_ai_source": simulation.content_analysis_ai_source,
        "personas_ai_source": simulation.personas_ai_source,
        "reasons_ai_source": simulation.reasons_ai_source,
    }


@router.get("/{simulation_id}/metrics")
def get_metrics(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    return {
        "virality_score": simulation.virality_score,
        "predicted_reach": simulation.predicted_reach,
        "like_rate": simulation.like_rate,
        "comment_rate": simulation.comment_rate,
        "share_rate": simulation.share_rate,
        "cascade_depth": simulation.cascade_depth,
        "final_verdict": simulation.final_verdict,
    }


@router.get("/{simulation_id}/graph", response_model=SimulationGraphResponse)
def get_graph(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    personas = db.query(Persona).filter(Persona.simulation_id == simulation.id).all()
    persona_index = {persona.id: index for index, persona in enumerate(personas)}
    decisions = {
        decision.persona_id: decision
        for decision in db.query(AgentDecision).filter(AgentDecision.simulation_id == simulation.id).all()
    }
    graph = nx.Graph()
    for persona in personas:
        graph.add_node(persona.id)
    edge_rows = db.query(GraphEdge).filter(GraphEdge.simulation_id == simulation.id).all()
    for edge in edge_rows:
        if edge.source_persona_id:
            graph.add_edge(edge.source_persona_id, edge.target_persona_id, weight=edge.weight)
    layout = nx.spring_layout(graph, seed=42, weight="weight") if graph.nodes else {}

    nodes = []
    for persona in personas:
        decision = decisions.get(persona.id)
        action = "never_shown"
        if decision:
            action = "shared" if decision.shared else "commented" if decision.commented else "liked" if decision.liked else "watched" if decision.watched else "skipped"
        nodes.append(
            GraphNode(
                id=persona.id,
                label=persona.name,
                in_target=persona.in_target,
                status="engaged" if action in {"liked", "commented", "shared"} else action,
                action=action,
                round=decision.round_number if decision else None,
                x=float(layout.get(persona.id, (persona_index[persona.id], 0))[0]) * 420 + 460,
                y=float(layout.get(persona.id, (0, persona_index[persona.id]))[1]) * 210 + 250,
            )
        )

    edges = [
        GraphEdgeResponse(
            id=edge.id,
            source=edge.source_persona_id,
            target=edge.target_persona_id,
            type=edge.relationship_type,
            weight=edge.weight,
        )
        for edge in edge_rows
    ]
    return SimulationGraphResponse(nodes=nodes, edges=edges)


@router.get("/{simulation_id}/rounds")
def get_rounds(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    return db.query(SimulationRound).filter(SimulationRound.simulation_id == simulation.id).order_by(SimulationRound.round_number).all()


@router.get("/{simulation_id}/personas")
def get_personas(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    personas = db.query(Persona).filter(Persona.simulation_id == simulation.id).all()
    decisions = {
        decision.persona_id: decision
        for decision in db.query(AgentDecision).filter(AgentDecision.simulation_id == simulation.id).all()
    }

    response = []
    for persona in personas:
        decision = decisions.get(persona.id)
        action = "never_shown"
        if decision:
            action = (
                "shared"
                if decision.shared
                else "commented"
                if decision.commented
                else "liked"
                if decision.liked
                else "watched"
                if decision.watched
                else "skipped"
            )
        response.append(
            {
                "id": persona.id,
                "name": persona.name,
                "age": persona.age,
                "location": persona.location,
                "profession": persona.profession,
                "interests": persona.interests,
                "pain_points": persona.pain_points,
                "content_preferences": persona.content_preferences,
                "engagement_tendency": persona.engagement_tendency,
                "share_probability": persona.share_probability,
                "skepticism_level": persona.skepticism_level,
                "in_target": persona.in_target,
                "action": action,
                "reason": decision.reason if decision else "This persona was not reached during the simulation.",
                "round": decision.round_number if decision else None,
            }
        )
    return response


@router.get("/{simulation_id}/report")
def get_report(simulation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    simulation = get_simulation(simulation_id, db, current_user)
    report = db.query(Report).filter(Report.simulation_id == simulation.id).first()
    if not report:
        return None
    analysis = simulation.video.content_analysis if simulation.video else None
    return {
        "id": report.id,
        "simulation_id": report.simulation_id,
        "summary": report.summary,
        "improvement_suggestions": report.improvement_suggestions,
        "best_audience_segments": report.best_audience_segments,
        "risk_factors": report.risk_factors,
        "ml_verdict_prediction": report.ml_verdict_prediction,
        "visual_description": analysis.visual_description if analysis else None,
        "created_at": report.created_at,
    }
