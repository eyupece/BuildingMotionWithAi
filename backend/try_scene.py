"""Try a city scene on Veo without going through the app.

Takes an avatar that's already in the bucket (from a real run) and makes a
few videos side by side, so prompt changes can be compared quickly.

    cd ~/BuildingMotionWithAi/backend
    pip install -q google-genai google-cloud-storage pydantic-settings
    python3 try_scene.py <video_id> kastamonu
    python3 try_scene.py <video_id> kastamonu --background "on the castle walls at sunset..."

video_id is the one from the share link. Each run costs a few Veo generations.
"""

import argparse
import asyncio
import os
import sys
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

from app.config import settings  # noqa: E402
from app.prompts import video_generation  # noqa: E402
from app.services import veo_service  # noqa: E402

MOTION = {
    "veo_prompt": "The character waves at the camera with the right hand, then turns slightly and points to the city behind.",
    "overall_style": "smooth and friendly",
}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("location", nargs="?", default="kastamonu")
    ap.add_argument("--style", default="pixel-hero")
    ap.add_argument("--background", help="replace the location text for this run")
    ap.add_argument("--camera", help="replace the camera line for this run")
    args = ap.parse_args()

    loc = video_generation._LOCATION_META[args.location]
    if args.background:
        loc["background"] = args.background
    if args.camera:
        loc["camera"] = args.camera

    from google import genai

    client = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    avatar = f"gs://{settings.GCS_BUCKET}/avatars/{args.video_id}.png"
    prompt = video_generation.build_video_prompt(MOTION, args.style, args.location)
    print(f"Avatar: {avatar}\nPrompt:\n{prompt}\n")

    stamp = time.strftime("%H%M%S")
    runs = {}
    for use_scene in (True, False):
        name = f"tries/{args.location}-{stamp}-{'photo' if use_scene else 'text'}"
        if use_scene and not veo_service_scene(args.location):
            print("No photo in app/events/scenes/, only trying the text version.")
            continue
        runs[name] = await veo_service._generate_with_retry(
            client=client, prompt=prompt, avatar_image_gcs_uri=avatar,
            video_id=name, location_theme=args.location, use_scene=use_scene,
        )

    print("Generating, this takes a minute or two...")
    while runs:
        await asyncio.sleep(10)
        for name, op in list(runs.items()):
            op = client.operations.get(op)
            if not op.done:
                continue
            del runs[name]
            if op.error:
                print(f"{name}: failed, {op.error}")
                continue
            uri = op.result.generated_videos[0].video.uri
            path = uri.removeprefix("gs://")
            print(f"{name}: https://storage.cloud.google.com/{path}")


def veo_service_scene(location):
    from app.events import scene_image
    return scene_image(location) is not None


if __name__ == "__main__":
    asyncio.run(main())
