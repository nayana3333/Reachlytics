from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.transcript import Transcript
from app.models.user import User
from app.models.video import Video
from app.schemas.video import TranscriptResponse, VideoResponse
from app.services.video_service import save_upload

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=VideoResponse, status_code=201)
def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return save_upload(db, current_user.id, file)


@router.get("", response_model=list[VideoResponse])
def list_videos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Video).filter(Video.user_id == current_user.id).order_by(Video.created_at.desc()).all()


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Video).filter(Video.id == video_id, Video.user_id == current_user.id).one()


@router.get("/{video_id}/transcript", response_model=TranscriptResponse)
def get_transcript(video_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transcript = (
        db.query(Transcript)
        .join(Video)
        .filter(Transcript.video_id == video_id, Video.user_id == current_user.id)
        .one()
    )
    return transcript
