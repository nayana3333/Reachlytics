import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id: Mapped[str] = mapped_column(String, ForeignKey("simulations.id"))
    name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String(120))
    profession: Mapped[str] = mapped_column(String(120))
    interests: Mapped[list] = mapped_column(JSON, default=list)
    pain_points: Mapped[list] = mapped_column(JSON, default=list)
    content_preferences: Mapped[list] = mapped_column(JSON, default=list)
    engagement_tendency: Mapped[float] = mapped_column(Float)
    share_probability: Mapped[float] = mapped_column(Float)
    skepticism_level: Mapped[float] = mapped_column(Float)
    in_target: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    simulation = relationship("Simulation", back_populates="personas")
    decisions = relationship("AgentDecision", back_populates="persona")
