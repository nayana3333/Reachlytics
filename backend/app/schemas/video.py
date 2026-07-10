from datetime import datetime

from pydantic import BaseModel


class VideoResponse(BaseModel):
    id: str
    title: str
    filename: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptResponse(BaseModel):
    text: str
    language: str
    confidence: float
    ai_source: str
