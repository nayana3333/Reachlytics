import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id: Mapped[str] = mapped_column(String, ForeignKey("simulations.id"))
    persona_id: Mapped[str] = mapped_column(String, ForeignKey("personas.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    watched: Mapped[bool] = mapped_column(Boolean)
    liked: Mapped[bool] = mapped_column(Boolean)
    commented: Mapped[bool] = mapped_column(Boolean)
    shared: Mapped[bool] = mapped_column(Boolean)
    engagement_score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    simulation = relationship("Simulation", back_populates="decisions")
    persona = relationship("Persona", back_populates="decisions")
