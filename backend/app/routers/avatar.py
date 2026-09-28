import asyncio
from fastapi import APIRouter, HTTPException
from ..models.schemas import GenerateAvatarRequest, GenerateAvatarResponse
from ..config import settings
from ..services import nano_banana_service, storage_service, video_utils

router = APIRouter()


def _frame_from_upload(video_id: str) -> bytes:
    gcs_uri = f"gs://{settings.GCS_BUCKET}/uploads/{video_id}.webm"
    local_path = storage_service.download_to_temp(gcs_uri, video_id)
    frame_bytes = video_utils.extract_frame(local_path, "0:01")
    storage_service.upload_frame(video_id, frame_bytes)
    return frame_bytes


@router.post("/generate-avatar", response_model=GenerateAvatarResponse)
async def generate_avatar(request: GenerateAvatarRequest):
    # Load the extracted frame from GCS (saved during analysis step)
    try:
        frame_bytes = await asyncio.to_thread(storage_service.download_frame, request.video_id)
    except Exception:
        # Analysis didn't leave a frame behind, so pull one from the upload now
        try:
            frame_bytes = await asyncio.to_thread(_frame_from_upload, request.video_id)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Frame not found for video_id={request.video_id}",
            )

    # Generate avatar image with Gemini 3 Pro Image (Nano Banana 2)
    image_bytes = await nano_banana_service.generate_avatar_image(
        frame_bytes, request.avatar_style
    )

    # Save generated avatar to GCS at gs://{BUCKET}/avatars/{video_id}.png
    gcs_uri = await asyncio.to_thread(
        storage_service.upload_avatar, request.video_id, image_bytes
    )

    # Generate a signed URL for the avatar image
    signed_url = await asyncio.to_thread(
        storage_service.generate_signed_url, gcs_uri, request.video_id
    )

    return GenerateAvatarResponse(avatar_image_url=signed_url)
