"""Queue management for concurrent Veo generation jobs.

Tracks active video_id jobs so the kiosk frontend can check capacity
before starting a new session.
"""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import settings
from ..services import usage_service

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_CONCURRENT_JOBS = 3

# Active video_ids (jobs where Veo generation has started but composition isn't done)
_active_jobs: set[str] = set()


class QueueStatusResponse(BaseModel):
    active_jobs: int
    max_jobs: int
    available: bool
    limit_reached: bool = False


@router.get("/queue/status", response_model=QueueStatusResponse)
async def queue_status():
    """Check whether the kiosk has capacity for a new session."""
    try:
        limit_reached = await usage_service.limit_reached()
    except Exception:
        logger.exception("Could not read the video count")
        limit_reached = False
    return QueueStatusResponse(
        active_jobs=len(_active_jobs),
        max_jobs=MAX_CONCURRENT_JOBS,
        available=len(_active_jobs) < MAX_CONCURRENT_JOBS and not limit_reached,
        limit_reached=limit_reached,
    )


def register(video_id: str) -> None:
    """Mark a video_id as actively processing (called when Veo generation starts)."""
    _active_jobs.add(video_id)
    logger.info("Queue: registered %s (%d/%d active)", video_id, len(_active_jobs), MAX_CONCURRENT_JOBS)


def complete(video_id: str) -> None:
    """Mark a video_id as done (called when composition completes)."""
    _active_jobs.discard(video_id)
    logger.info("Queue: completed %s (%d/%d active)", video_id, len(_active_jobs), MAX_CONCURRENT_JOBS)
