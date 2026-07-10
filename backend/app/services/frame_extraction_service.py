from __future__ import annotations

import logging
from pathlib import Path
import uuid

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def extract_frames(video_path: str | Path, num_frames: int = 4) -> list[str]:
    """Extract evenly spaced JPEG frames from a video.

    Failures are intentionally non-fatal: callers should fall back to text-only
    analysis when the video codec, path, or OpenCV runtime is unavailable.
    """
    try:
        import cv2
    except Exception:
        logger.exception("OpenCV is not available; skipping video frame extraction")
        return []

    path = Path(video_path)
    if not path.exists():
        logger.warning("Video path does not exist; skipping frame extraction: %s", path)
        return []

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        logger.warning("OpenCV could not open video for frame extraction: %s", path)
        return []

    frame_paths: list[str] = []
    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if frame_count <= 0:
            logger.warning("Video has no readable frames: %s", path)
            return []

        percentages = [0.1, 0.4, 0.7, 0.9]
        if num_frames != 4:
            percentages = [(index + 1) / (num_frames + 1) for index in range(num_frames)]

        output_dir = Path(get_settings().upload_dir) / "frames" / str(uuid.uuid4())
        output_dir.mkdir(parents=True, exist_ok=True)
        for index, percentage in enumerate(percentages[:num_frames], start=1):
            frame_index = min(frame_count - 1, max(0, int(frame_count * percentage)))
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = capture.read()
            if not success or frame is None:
                logger.warning("Could not read frame %s from %s", frame_index, path)
                continue

            output_path = output_dir / f"frame_{index:02d}.jpg"
            success, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
            if success:
                output_path.write_bytes(encoded.tobytes())
                frame_paths.append(str(output_path))
            else:
                logger.warning("Could not encode extracted frame %s from %s", frame_index, path)
    except Exception:
        logger.exception("Frame extraction failed for %s", path)
        return []
    finally:
        capture.release()

    return frame_paths
