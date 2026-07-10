from datetime import datetime

from pydantic import BaseModel, Field


class SimulationCreate(BaseModel):
    video_id: str
    target_audience: str = Field(min_length=10)
    persona_count: int = Field(default=100, ge=50, le=500)
    round_count: int = Field(default=5, ge=3, le=10)


class SimulationResponse(BaseModel):
    id: str
    video_id: str
    target_audience: str
    persona_count: int
    round_count: int
    status: str
    progress_stage: str = "queued"
    error_message: str | None = None
    transcript_ai_source: str = "fallback"
    content_analysis_ai_source: str = "fallback"
    personas_ai_source: str = "fallback"
    reasons_ai_source: str = "fallback"
    virality_score: float | None = None
    predicted_reach: int | None = None
    like_rate: float | None = None
    comment_rate: float | None = None
    share_rate: float | None = None
    cascade_depth: int | None = None
    final_verdict: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class GraphNode(BaseModel):
    id: str
    label: str
    in_target: bool
    status: str
    action: str
    round: int | None = None
    x: float | None = None
    y: float | None = None


class GraphEdgeResponse(BaseModel):
    id: str
    source: str | None
    target: str
    type: str
    weight: float


class SimulationGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdgeResponse]
