"""Event poster kit: the attendee ends up inside the DevFest poster.

The poster itself never goes through AI. Nano Banana only draws the person for
the empty spot (the cloth on the loom, the gold frame), Veo animates that
portrait from its first frame, and the result is pasted back into the poster.
"""

import asyncio
import io
import logging
import os
import random
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..config import settings
from ..events import EVENTS

logger = logging.getLogger(__name__)

POSTERS: dict[str, dict] = {e.POSTER_KEY: e.POSTER for e in EVENTS.values() if hasattr(e, "POSTER_KEY")}

_IMAGES = Path(__file__).resolve().parent.parent / "events" / "posters"

_KEEP = (
    "Keep the person clearly recognizable: same face, hair, glasses and beard if any. "
    "No text, no border, no picture frame, just the scene."
)

# video_id → poster key, so the trim step knows to paste the video back
_videos: dict[str, str] = {}


def is_poster(style_key: str) -> bool:
    return style_key in POSTERS


def _poster(key: str) -> Image.Image:
    return Image.open(_IMAGES / POSTERS[key]["image"]).convert("RGB")


def _png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _fit(img: Image.Image, w: int, h: int) -> Image.Image:
    """Center-crop to w:h and resize."""
    img = img.convert("RGB")
    sw, sh = img.size
    if sw / sh > w / h:
        nw = round(sh * w / h)
        img = img.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = round(sw * h / w)
        img = img.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return img.resize((w, h), Image.LANCZOS)


def _mask(poster: dict) -> Image.Image:
    _, _, w, h = poster["slot"]
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    if poster["woven"]:
        # soft edges so it melts into the cloth
        d.rectangle((14, 14, w - 15, h - 15), fill=255)
        return m.filter(ImageFilter.GaussianBlur(10))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    return m.filter(ImageFilter.GaussianBlur(1))


async def draw_portrait(frame_bytes: bytes, key: str) -> bytes:
    """Draw the person for the poster's empty spot, as a 9:16 image Veo can start from."""
    if settings.MOCK_AI:
        await asyncio.sleep(2)
        return _png(Image.new("RGB", (576, 1024), (120, 90, 60)))

    from google.genai import types

    from . import nano_banana_service as nb

    poster = POSTERS[key]
    x, y, w, h = poster["slot"]
    spot = _poster(key).crop((x, y, x + w, y + h))
    prompt = (
        f"Image 1 is a photo of a person. Image 2 is an empty part of a poster. "
        f"{poster['portrait'].format(outfit=random.choice(poster.get('outfits') or ['']))} {_KEEP}"
    )
    response = await asyncio.to_thread(
        nb._get_client().models.generate_content,
        model=nb._MODELS[0],
        contents=[types.Content(role="user", parts=[
            types.Part.from_bytes(data=frame_bytes, mime_type="image/png"),
            types.Part.from_bytes(data=_png(spot), mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ])],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16", output_mime_type="image/png"),
        ),
    )
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
    raise ValueError("Gemini returned no image in response")


def paste_still(portrait_bytes: bytes, key: str) -> bytes:
    """The poster with the portrait in its spot, as PNG bytes."""
    poster = POSTERS[key]
    x, y, w, h = poster["slot"]
    out = _poster(key)
    portrait = Image.open(io.BytesIO(portrait_bytes))
    art = _fit(portrait, w, h)
    if poster["woven"]:
        # multiply keeps the cloth texture and the border patterns on top
        art = Image.blend(ImageChops.multiply(art, out.crop((x, y, x + w, y + h))), art, 0.35)
    out.paste(art, (x, y), _mask(poster))
    return _png(out)


def build_video_prompt(motion_analysis: dict[str, Any], key: str) -> str:
    from ..prompts.video_generation import _build_choreography

    art = POSTERS[key]["art"]
    moves = motion_analysis.get("veo_prompt") or "waves at the camera and smiles"
    choreography = _build_choreography(motion_analysis.get("phases", []))
    prompt = (
        f"The first frame is {art}. The person in it comes to life and does these moves, "
        f"starting right away from the first frame: {moves} "
    )
    if choreography:
        prompt += f"Exact timing for the first 3 seconds: {choreography} "
    if POSTERS[key].get("video_rules"):
        prompt += POSTERS[key]["video_rules"] + " "
    return prompt + (
        "Always exactly two hands. Only the person moves: head, face, arms and hands. "
        f"The background stays still. Keep the exact look of the first frame, still {art}, "
        "for the whole video. Static camera, no zoom, no cuts."
    )


def remember(video_id: str, key: str) -> None:
    """Note that this video belongs on a poster, here and in the bucket."""
    _videos[video_id] = key
    if settings.MOCK_AI:
        return
    from google.cloud import storage as gcs

    bucket = gcs.Client(project=settings.GOOGLE_CLOUD_PROJECT).bucket(settings.GCS_BUCKET)
    bucket.blob(f"avatars/{video_id}.poster").upload_from_string(key, content_type="text/plain")


def poster_for(video_id: str) -> str | None:
    if video_id in _videos or settings.MOCK_AI:
        return _videos.get(video_id)
    # The status poll can land on another instance than the one that drew the avatar
    from google.cloud import storage as gcs

    blob = gcs.Client(project=settings.GOOGLE_CLOUD_PROJECT).bucket(settings.GCS_BUCKET).blob(
        f"avatars/{video_id}.poster"
    )
    if not blob.exists():
        return None
    key = blob.download_as_text().strip()
    if key in POSTERS:
        _videos[video_id] = key
        return key
    return None


def paste_video(video_path: str, key: str, seconds: float = 3.0) -> str:
    """Paste a Veo clip into the poster. Returns the path to a new temp .mp4."""
    from .video_utils import _ffmpeg_exe

    poster = POSTERS[key]
    x, y, w, h = poster["slot"]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.close()
    with tempfile.TemporaryDirectory() as d:
        mask = os.path.join(d, "mask.png")
        _mask(poster).save(mask)
        fit = f"crop=min(iw\\,ih*{w}/{h}):min(ih\\,iw*{h}/{w}),scale={w}:{h},setsar=1"
        if poster["woven"]:
            graph = (
                f"[0:v]split[p][q];[q]crop={w}:{h}:{x}:{y},format=gbrp[bg];"
                f"[1:v]{fit},format=gbrp,split[v][v2];"
                f"[v][bg]blend=all_mode=multiply[mul];[mul][v2]blend=all_expr='A*0.65+B*0.35',format=rgba[art];"
            )
        else:
            graph = f"[0:v]copy[p];[1:v]{fit},format=rgba[art];"
        graph += f"[2:v]format=gray[m];[art][m]alphamerge[am];[p][am]overlay={x}:{y}:shortest=1,format=yuv420p"
        subprocess.run([
            _ffmpeg_exe(), "-y",
            "-loop", "1", "-i", str(_IMAGES / poster["image"]),
            "-i", video_path,
            "-loop", "1", "-i", mask,
            "-filter_complex", graph,
            # the poster and mask loop forever, so stop at the clip's length
            "-t", str(seconds),
            "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            tmp.name,
        ], check=True, capture_output=True)
    return tmp.name


def maybe_paste(video_path: str, video_id: str | None) -> str:
    """Put the clip into the poster if this video came from the poster kit.

    Returns the path to upload: the same one, or a new temp file the caller deletes.
    """
    key = poster_for(video_id) if video_id else None
    if not key:
        return video_path
    try:
        return paste_video(video_path, key)
    except Exception:
        logger.exception("Pasting into the %s poster failed for video_id=%s", key, video_id)
        return video_path
