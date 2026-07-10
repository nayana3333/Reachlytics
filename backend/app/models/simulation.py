import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String, ForeignKey("videos.id"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    target_audience: Mapped[str] = mapped_column(Text)
    persona_count: Mapped[int] = mapped_column(Integer)
    round_count: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    progress_stage: Mapped[str] = mapped_column(String(80), default="queued")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    personas_ai_source: Mapped[str] = mapped_column(String(20), default="fallback")
    reasons_ai_source: Mapped[str] = mapped_column(String(20), default="fallback")
    virality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    share_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    cascade_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_verdict: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    video = relationship("Video", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    personas = relationship("Persona", back_populates="simulation")
    decisions = relationship("AgentDecision", back_populates="simulation")
    edges = relationship("GraphEdge", back_populates="simulation")
    rounds = relationship("SimulationRound", back_populates="simulation")
    report = relationship("Report", back_populates="simulation", uselist=False)


class SimulationRound(Base):
    __tablename__ = "simulation_rounds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id: Mapped[str] = mapped_column(String, ForeignKey("simulations.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    active_agents: Mapped[int] = mapped_column(Integer)
    new_reach: Mapped[int] = mapped_column(Integer)
    likes: Mapped[int] = mapped_column(Integer)
    comments: Mapped[int] = mapped_column(Integer)
    shares: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    simulation = relationship("Simulation", back_populates="rounds")
