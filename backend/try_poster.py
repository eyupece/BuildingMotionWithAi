"""Try a new poster look outside the app.

Uses the app's own code (same paste, same 5 seconds, same camera move), only
the prompts come from DRAFTS below. When a draft looks good, copy it into
app/events/<city>.py.

    cd ~/BuildingMotionWithAi/backend
    pip install -q google-genai google-cloud-storage pydantic-settings pillow imageio-ffmpeg
    python3 try_poster.py kastamonu <video_id> [<video_id> ...]   # 2 stills per person
    python3 try_poster.py kastamonu <video_id> --video 1           # still 1 comes to life

video_id is the one from the share link. Stills are cheap, each video is one
Veo run and uses that recording's moves.
"""

import argparse
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
env = ROOT.parent / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(ROOT))

TRIES = ROOT / "tries"

DRAFTS = {
    # the poster's own warm engraving look instead of cross-stitch
    "kastamonu": {
        "key": "kastamonu-afis",
        "art": "a warm engraving-style illustration woven into a cream kilim cloth on a loom",
        "portrait": (
            "Draw the person onto the cream cloth of image 2 as a picture woven into the kilim, in the same "
            "style as a warm old storybook engraving: fine dark brown ink lines with cross-hatching, soft sepia "
            "shading and muted rust red, indigo blue, mustard and moss green, the cloth texture showing through. "
            "Draw them sitting upright and facing the viewer, even if the photo is tilted, taken from below "
            "or they are lying down. "
            "Waist-up, filling the width of the picture, centered, head in the upper third. "
            "Both hands fully visible, resting in front of the body in the lower part."
        ),
        "video_rules": (
            "A hand that rises is one of the two resting hands and leaves its place, so the person never "
            "has more than two hands. The hands stay at the same distance as the body, never come toward "
            "the camera and never cover the face. Every moving part keeps the same ink lines and color "
            "wash as the rest of the drawing."
        ),
        # more of the drawing over the cloth, the old 0.35 washed it out
        "keep": 0.6,
    },
}


def use_draft(city: str) -> str:
    """Swap the draft into the app's poster settings for this run only."""
    from app.services import poster_service

    draft = dict(DRAFTS[city])
    key = draft.pop("key")
    poster_service.POSTERS[key] = {**poster_service.POSTERS[key], **draft}
    return key


async def make_stills(args, key, settings, bucket):
    from app.services import poster_service

    TRIES.mkdir(exist_ok=True)
    stamp = time.strftime("%H%M%S")
    for video_id in args.video_ids:
        frame = bucket.blob(f"frames/{video_id}.png").download_as_bytes()
        # Nano Banana gives something different each run, so look at more than one
        for n in range(1, args.n + 1):
            print(f"{video_id[:8]} {n}: drawing...")
            portrait = await poster_service.draw_portrait(frame, key)
            (TRIES / f"{args.city}-{video_id}-{n}.png").write_bytes(portrait)
            name = f"tries/{args.city}-{stamp}-{video_id[:8]}-{n}.png"
            bucket.blob(name).upload_from_string(poster_service.paste_still(portrait, key), content_type="image/png")
            print(f"  https://storage.cloud.google.com/{settings.GCS_BUCKET}/{name}")
    print(f"\nTo see one move: python3 try_poster.py {args.city} {args.video_ids[0]} --video 1")


async def make_video(args, key, settings, bucket):
    from google import genai
    from google.genai.types import GenerateVideosConfig, Image as VeoImage

    from app.services import poster_service
    from app.services.gemini_service import analyze_video_sync

    video_id = args.video_ids[0]
    still = TRIES / f"{args.city}-{video_id}-{args.video}.png"
    if not still.exists():
        sys.exit(f"Make the stills first, {still.name} is missing.")

    print("Reading the moves from the recording...")
    moves = await asyncio.to_thread(analyze_video_sync, f"gs://{settings.GCS_BUCKET}/uploads/{video_id}.webm")
    prompt = poster_service.build_video_prompt(moves, key)
    print(f"Prompt:\n{prompt}\n")

    client = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    out = f"tries/{args.city}-{time.strftime('%H%M%S')}-{video_id[:8]}-{args.video}/"
    op = client.models.generate_videos(
        model="veo-3.1-fast-generate-001",
        prompt=prompt,
        image=VeoImage(image_bytes=still.read_bytes(), mime_type="image/png"),
        config=GenerateVideosConfig(
            aspect_ratio="9:16",
            duration_seconds=8,
            generate_audio=False,
            person_generation="allow_adult",
            output_gcs_uri=f"gs://{settings.GCS_BUCKET}/{out}",
        ),
    )
    print("Veo is working, a minute or two...")
    while not op.done:
        await asyncio.sleep(10)
        op = client.operations.get(op)
    if op.error or not op.result or not op.result.generated_videos:
        sys.exit(f"Veo failed: {op.error or 'no video (maybe blocked by the safety filter)'}")

    raw = op.result.generated_videos[0].video.uri.removeprefix(f"gs://{settings.GCS_BUCKET}/")
    with tempfile.TemporaryDirectory() as tmp:
        local = Path(tmp) / "in.mp4"
        bucket.blob(raw).download_to_filename(local)
        pasted = poster_service.paste_video(str(local), key)
        name = f"{out}poster.mp4"
        bucket.blob(name).upload_from_filename(pasted, content_type="video/mp4")
        os.unlink(pasted)
    print(f"On the poster: https://storage.cloud.google.com/{settings.GCS_BUCKET}/{name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("city", choices=list(DRAFTS))
    ap.add_argument("video_ids", nargs="+")
    ap.add_argument("--n", type=int, default=2, help="stills per person")
    ap.add_argument("--video", help="animate this still (1, 2...)")
    args = ap.parse_args()

    from google.cloud import storage

    from app.config import settings

    key = use_draft(args.city)
    bucket = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT).bucket(settings.GCS_BUCKET)
    if args.video:
        asyncio.run(make_video(args, key, settings, bucket))
    else:
        asyncio.run(make_stills(args, key, settings, bucket))


if __name__ == "__main__":
    main()
