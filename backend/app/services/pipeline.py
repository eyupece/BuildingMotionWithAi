"""Background pipeline that drives a video job to completion autonomously.

After Veo generation starts, this pipeline runs in the background:
  1. Poll Veo operation until complete
  2. Download raw video → trim to 3s → upload trimmed
  3. Download original + trimmed → compose side-by-side → upload composed
  4. Mark queue slot as complete

This ensures the mobile share page works even when the kiosk has moved on.
"""

import asyncio
import logging
import os

from ..config import settings
from . import poster_service, storage_service, veo_service, video_utils

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 5
_MAX_POLL_ATTEMPTS = 120  # 10 min max
_TRIM_DURATION_S = video_utils.CLIP_SECONDS

# Track which video_ids have an active pipeline task (prevents duplicates)
_running_pipelines: set[str] = set()

# Strong references to background tasks — prevents GC from killing them.
# See: https://docs.python.org/3/library/asyncio-task.html#creating-tasks
_background_tasks: set[asyncio.Task] = set()


def is_running(video_id: str) -> bool:
    """Check if a pipeline task is already running for this video_id."""
    return video_id in _running_pipelines


def spawn(operation_id: str, video_id: str) -> None:
    """Create a background pipeline task with a strong reference."""
    task = asyncio.create_task(run_pipeline(operation_id, video_id))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def run_pipeline(operation_id: str, video_id: str) -> None:
    """Run the full post-generation pipeline in the background.

    This is fire-and-forget — errors are logged but never raised.
    """
    if video_id in _running_pipelines:
        logger.warning("Pipeline already running for video_id=%s, skipping", video_id)
        return

    _running_pipelines.add(video_id)
    try:
        logger.info("Pipeline started for video_id=%s op=%s", video_id, operation_id)

        # ── Step 1: Poll Veo until complete ────────────────────────────────
        gcs_uri = await _poll_until_complete(operation_id, video_id)
        if not gcs_uri:
            logger.error("Pipeline: Veo failed or timed out for video_id=%s", video_id)
            return

        # ── Step 2: Trim to 3s ─────────────────────────────────────────────
        trimmed_gcs_uri = await _trim_video(gcs_uri, video_id)

        # ── Step 3: Compose side-by-side ───────────────────────────────────
        await _compose_video(trimmed_gcs_uri or gcs_uri, video_id)

        logger.info("Pipeline complete for video_id=%s", video_id)
    except Exception:
        logger.exception("Pipeline failed for video_id=%s", video_id)
    finally:
        _running_pipelines.discard(video_id)
        _complete_queue(video_id)


def _complete_queue(video_id: str) -> None:
    """Release the queue slot."""
    from ..routers import queue as queue_tracker
    queue_tracker.complete(video_id)


async def _poll_until_complete(operation_id: str, video_id: str) -> str | None:
    """Poll the Veo operation and return the output GCS URI, or None on failure."""
    for attempt in range(1, _MAX_POLL_ATTEMPTS + 1):
        await asyncio.sleep(_POLL_INTERVAL_S)

        result = await veo_service.poll_operation(operation_id)
        status = result["status"]

        if status == "processing":
            if attempt % 12 == 0:  # Log every ~60s
                logger.info("Pipeline: still polling for video_id=%s (%ds)", video_id, attempt * _POLL_INTERVAL_S)
            continue

        if status == "complete" and result.get("gcs_uri"):
            logger.info("Pipeline: Veo complete for video_id=%s → %s", video_id, result["gcs_uri"])
            return result["gcs_uri"]

        # Failed
        logger.error("Pipeline: Veo failed for video_id=%s: %s", video_id, result.get("error"))
        return None

    logger.error("Pipeline: Veo poll timed out for video_id=%s after %ds", video_id, _MAX_POLL_ATTEMPTS * _POLL_INTERVAL_S)
    return None


# video_id -> trimmed GCS URI, shared with the status endpoint
trimmed_uris: dict[str, str] = {}


def trim_sync(gcs_uri: str, video_id: str) -> str | None:
    """Download raw Veo output, trim, put it on the poster if needed, upload.

    Blocking (ffmpeg), so call it from a thread. Runs once per video even when
    the pipeline and a status poll ask at the same time.
    """
    if settings.MOCK_AI:
        return None
    with video_utils.video_lock(f"trim:{video_id}"):
        if video_id in trimmed_uris:
            return trimmed_uris[video_id]
        done = f"gs://{settings.GCS_BUCKET}/output/{video_id}/trimmed_3s.mp4"
        if storage_service.gcs_blob_exists(done):
            trimmed_uris[video_id] = done
            return done

        local_full: str | None = None
        local_trimmed: str | None = None
        local_poster: str | None = None
        try:
            local_full = storage_service.download_gcs_video(gcs_uri)
            local_trimmed = video_utils.trim_video(local_full, _TRIM_DURATION_S)
            local_poster = poster_service.maybe_paste(local_trimmed, video_id)

            with open(local_poster, "rb") as f:
                trimmed_data = f.read()

            trimmed_gcs_uri = storage_service.upload_trimmed_video(video_id, trimmed_data)
            trimmed_uris[video_id] = trimmed_gcs_uri
            logger.info("Pipeline: trimmed video uploaded for video_id=%s", video_id)
            return trimmed_gcs_uri
        except Exception:
            logger.exception("Pipeline: trim failed for video_id=%s, will use raw video", video_id)
            return None
        finally:
            for path in {local_full, local_trimmed, local_poster}:
                if path:
                    try:
                        os.unlink(path)
                    except OSError:
                        pass


async def _trim_video(gcs_uri: str, video_id: str) -> str | None:
    """Trim in a thread so the server keeps answering polls meanwhile."""
    if settings.MOCK_AI:
        # In mock mode, just mark as "trimmed" — skip actual file operations
        trimmed_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/trimmed_3s.mp4"
        logger.info("Pipeline MOCK: skip trim for video_id=%s", video_id)
        return trimmed_uri
    return await asyncio.to_thread(trim_sync, gcs_uri, video_id)


async def _compose_video(generated_gcs_uri: str, video_id: str) -> None:
    """Compose in a thread (same code and lock as the share page)."""
    if settings.MOCK_AI:
        # In mock mode, store a mock composed URI in the cache
        mock_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/composed.mp4"
        storage_service._composed_cache[video_id] = mock_uri
        logger.info("Pipeline MOCK: composed cache set for video_id=%s", video_id)
        return

    from ..routers.share import compose_sync

    try:
        await asyncio.to_thread(compose_sync, video_id, generated_gcs_uri)
        logger.info("Pipeline: composed video ready for video_id=%s", video_id)
    except Exception:
        logger.exception("Pipeline: composition failed for video_id=%s", video_id)
