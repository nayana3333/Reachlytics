import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ContentAnalysis(Base):
    __tablename__ = "content_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String, ForeignKey("videos.id"), unique=True)
    hook_score: Mapped[float] = mapped_column(Float)
    clarity_score: Mapped[float] = mapped_column(Float)
    emotional_appeal_score: Mapped[float] = mapped_column(Float)
    shareability_score: Mapped[float] = mapped_column(Float)
    audience_fit_score: Mapped[float] = mapped_column(Float)
    product_category: Mapped[str] = mapped_column(String(120))
    summary: Mapped[str] = mapped_column(Text)
    visual_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)
    ai_source: Mapped[str] = mapped_column(String(20), default="fallback")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="content_analysis")
