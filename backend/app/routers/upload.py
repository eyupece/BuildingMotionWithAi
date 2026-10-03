import logging
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from ..models.schemas import UploadResponse
from ..services import storage_service
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _base_url(request: Request) -> str:
    # The share page lives on this backend, so build the link from the address the
    # upload came in on. PUBLIC_BASE_URL was easy to get wrong and pointed the QR
    # at the frontend, which just opens the start screen.
    host = request.headers.get("host")
    if not host or host.startswith(("localhost", "127.0.0.1")):
        return settings.PUBLIC_BASE_URL
    proto = request.headers.get("x-forwarded-proto", "https")
    return f"{proto}://{host}"


@router.post("/upload", response_model=UploadResponse)
async def upload_video(request: Request, file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    video_id = str(uuid.uuid4())
    share_url = f"{_base_url(request)}/share/{video_id}"
    print(f"\n{'='*60}")
    print(f"  NEW VIDEO: {video_id}")
    print(f"  Share page: {share_url}")
    print(f"{'='*60}\n")
    gcs_uri = storage_service.upload_video(video_id, data)

    return UploadResponse(video_id=video_id, gcs_uri=gcs_uri, share_url=share_url)
