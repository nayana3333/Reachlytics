import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id: Mapped[str] = mapped_column(String, ForeignKey("simulations.id"))
    source_persona_id: Mapped[str | None] = mapped_column(String, ForeignKey("personas.id"), nullable=True)
    target_persona_id: Mapped[str] = mapped_column(String, ForeignKey("personas.id"))
    weight: Mapped[float] = mapped_column(Float)
    relationship_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    simulation = relationship("Simulation", back_populates="edges")
