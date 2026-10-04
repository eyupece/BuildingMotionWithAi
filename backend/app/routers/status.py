import asyncio
import logging

from fastapi import APIRouter

from ..models.schemas import StatusResponse
from ..services import pipeline, veo_service, storage_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status/{operation_id}", response_model=StatusResponse)
async def get_status(operation_id: str):
    result = await veo_service.poll_operation(operation_id)

    status = result["status"]

    if status == "processing":
        return StatusResponse(status="processing")

    if status == "failed":
        return StatusResponse(status="failed", error=result.get("error"))

    # status == "complete"
    gcs_uri: str | None = result.get("gcs_uri")
    video_id: str | None = result.get("video_id")

    if gcs_uri:
        # Trim (and put on the poster) in a thread, shared with the background
        # pipeline, so the server keeps answering everyone else meanwhile.
        trimmed = await asyncio.to_thread(pipeline.trim_sync, gcs_uri, video_id) if video_id else None
        try:
            signed_url = await asyncio.to_thread(storage_service.generate_video_signed_url, trimmed or gcs_uri)
            return StatusResponse(status="complete", result_url=signed_url)
        except Exception as exc:  # noqa: BLE001
            return StatusResponse(
                status="failed",
                error=f"Signed URL generation failed: {exc}",
            )

    # No GCS URI — this shouldn't happen; report failure so the user can retry
    return StatusResponse(
        status="failed",
        error="Video generation completed but no output was found. Please try again.",
    )
