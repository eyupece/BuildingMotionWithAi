"""How many Veo videos were started today.

The free trial credit runs out after about 30 videos, so the app stops at VIDEO_LIMIT.
The count lives in Cloud Storage (one file per Turkey day) so a restart doesn't reset it.
To start over during the day, delete limits/videos-<date>.txt from the bucket.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from ..config import settings

_lock = asyncio.Lock()
_mock_counts: dict[str, int] = {}


def _blob_name() -> str:
    today = datetime.now(timezone(timedelta(hours=3)))
    return f"limits/videos-{today:%Y-%m-%d}.txt"


def _blob():
    from google.cloud import storage as gcs

    client = gcs.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    return client.bucket(settings.GCS_BUCKET).blob(_blob_name())


def _read() -> int:
    if settings.MOCK_AI:
        return _mock_counts.get(_blob_name(), 0)
    blob = _blob()
    if not blob.exists():
        return 0
    try:
        return int(blob.download_as_text().strip() or 0)
    except ValueError:
        return 0


def _write(count: int) -> None:
    if settings.MOCK_AI:
        _mock_counts[_blob_name()] = count
        return
    _blob().upload_from_string(str(count), content_type="text/plain")


async def count() -> int:
    return await asyncio.to_thread(_read)


async def limit_reached() -> bool:
    if settings.VIDEO_LIMIT <= 0:
        return False
    return await count() >= settings.VIDEO_LIMIT


async def add_one() -> int:
    async with _lock:
        n = await asyncio.to_thread(_read) + 1
        await asyncio.to_thread(_write, n)
        return n
