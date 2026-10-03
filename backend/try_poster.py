"""Put someone into the DevFest poster, outside the app.

The poster itself never goes through AI. Nano Banana only draws the person
for the empty spot (the cloth on the loom, the gold frame), Veo animates that
portrait, and the result is pasted back into the original poster.

    cd ~/BuildingMotionWithAi/backend
    pip install -q google-genai google-cloud-storage pydantic-settings pillow imageio-ffmpeg
    python3 try_poster.py <video_id> trabzon            # 3 stills on the poster
    python3 try_poster.py <video_id> trabzon --video b  # still b comes to life

video_id is the one from the share link. Stills are cheap, each video is one
Veo run and uses that recording's moves.
"""

import argparse
import asyncio
import io
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
env = ROOT.parent / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(ROOT))

POSTERS = ROOT / "app" / "events" / "posters"
TRIES = ROOT / "tries"

KEEP = (
    "Keep the person clearly recognizable: same face, hair, glasses and beard if any. "
    "Waist-up and a little small in the picture, centered, with space on every side. "
    "Both hands fully visible, resting in front of the body in the lower part, so arm and hand moves "
    "stay inside the picture. No text, no border, no picture frame, just the scene."
)

CITIES = {
    "kastamonu": {
        # x, y, w, h of the empty cloth on the loom
        "slot": (468, 482, 232, 338),
        "woven": True,
        "art": "a portrait woven into a cream kilim cloth on a loom",
        "styles": {
            "a": "Weave the person into the cream cloth of image 2 as a hand-woven kilim: visible threads, "
                 "flat stepped kilim shapes, only cream, rust red, indigo blue, mustard and moss green.",
            "b": "Draw the person on the cream cloth of image 2 in the same style as a warm old illustration: "
                 "fine ink lines with a soft sepia and warm color wash, the cloth texture showing through.",
            "c": "Stitch the person onto the cream linen of image 2 as cross-stitch embroidery in rust red, "
                 "indigo blue, mustard and moss green thread.",
        },
    },
    "trabzon": {
        # x, y, w, h of the canvas inside the gold frame
        "slot": (388, 353, 350, 494),
        "woven": False,
        "art": "an old master oil painting",
        "styles": {
            "a": "Paint the person into image 2 as a Rembrandt oil portrait, wearing their own clothes painted "
                 "in oil. Warm light from the upper left, deep shadows, visible brushwork. Keep the dark "
                 "background, the red curtain on the right and the column.",
            "b": "Paint the person into image 2 as a 17th century Dutch portrait in a black doublet with a large "
                 "white lace collar. Warm light from the upper left, visible brushwork. Keep the dark "
                 "background, the red curtain on the right and the column.",
            "c": "Paint the person into image 2 as a Velazquez portrait in a dark cloak. Soft light, loose "
                 "brushwork. Keep the dark background, the red curtain on the right and the column.",
        },
    },
}


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


def _mask(city: dict) -> Image.Image:
    _, _, w, h = city["slot"]
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    if city["woven"]:
        # soft edges so it melts into the cloth
        d.rectangle((14, 14, w - 15, h - 15), fill=255)
        return m.filter(ImageFilter.GaussianBlur(10))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    return m.filter(ImageFilter.GaussianBlur(1))


def paste(poster: Image.Image, portrait: Image.Image, city: dict) -> Image.Image:
    x, y, w, h = city["slot"]
    out = poster.convert("RGB").copy()
    art = _fit(portrait, w, h)
    if city["woven"]:
        # multiply keeps the cloth texture and the border patterns on top
        art = ImageChops.multiply(art, out.crop((x, y, x + w, y + h)))
        art = Image.blend(art, _fit(portrait, w, h), 0.35)
    out.paste(art, (x, y), _mask(city))
    return out


def _png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def make_stills(args, city, poster, settings, bucket):
    from google.genai import types

    from app.services import nano_banana_service as nb

    frame = bucket.blob(f"frames/{args.video_id}.png").download_as_bytes()
    x, y, w, h = city["slot"]
    spot = poster.crop((x, y, x + w, y + h))
    TRIES.mkdir(exist_ok=True)
    client = nb._get_client()
    stamp = time.strftime("%H%M%S")

    for key, style in city["styles"].items():
        if args.only and key != args.only:
            continue
        prompt = f"Image 1 is a photo of a person. Image 2 is an empty part of a poster. {style} {KEEP}"
        print(f"{key}: drawing...")
        resp = client.models.generate_content(
            model=nb._MODELS[0],
            contents=[types.Content(role="user", parts=[
                types.Part.from_bytes(data=frame, mime_type="image/png"),
                types.Part.from_bytes(data=_png(spot), mime_type="image/png"),
                types.Part.from_text(text=prompt),
            ])],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
            ),
        )
        data = next((p.inline_data.data for c in resp.candidates for p in c.content.parts if p.inline_data), None)
        if not data:
            print(f"{key}: no image came back")
            continue
        portrait = Image.open(io.BytesIO(data))
        portrait.save(TRIES / f"{args.city}-{key}.png")
        name = f"tries/poster-{args.city}-{stamp}-{key}.png"
        bucket.blob(name).upload_from_string(_png(paste(poster, portrait, city)), content_type="image/png")
        print(f"{key}: https://storage.cloud.google.com/{settings.GCS_BUCKET}/{name}")

    print(f"\nTo see one move: python3 try_poster.py {args.video_id} {args.city} --video a")


async def make_video(args, city, poster, settings, bucket):
    from google import genai
    from google.genai.types import GenerateVideosConfig, Image as VeoImage

    from app.prompts.video_generation import _build_choreography
    from app.services.gemini_service import analyze_video_sync

    still = TRIES / f"{args.city}-{args.video}.png"
    if not still.exists():
        sys.exit(f"Make the stills first, {still.name} is missing.")

    print("Reading the moves from the recording...")
    moves = await asyncio.to_thread(analyze_video_sync, f"gs://{settings.GCS_BUCKET}/uploads/{args.video_id}.webm")
    choreo = _build_choreography(moves.get("phases", []))
    prompt = (
        f"The first frame is {city['art']}. The person in it comes to life and does these moves, "
        f"starting right away: {moves.get('veo_prompt', '')} "
        + (f"Timing: {choreo} " if choreo else "")
        + "Always exactly two hands. "
        "Only the person moves: head, face, arms and hands. The background stays still. "
        f"Keep the exact look of the first frame, still {city['art']}, for the whole video. "
        "Static camera, no zoom, no cuts."
    )
    print(f"Prompt:\n{prompt}\n")

    client = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    stamp = time.strftime("%H%M%S")
    out = f"tries/poster-{args.city}-{stamp}-{args.video}/"
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
    print(f"Raw video: https://storage.cloud.google.com/{settings.GCS_BUCKET}/{raw}")

    import imageio_ffmpeg

    x, y, w, h = city["slot"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bucket.blob(raw).download_to_filename(tmp / "in.mp4")
        poster.convert("RGB").save(tmp / "poster.png")
        _mask(city).save(tmp / "mask.png")
        fit = f"crop=min(iw\\,ih*{w}/{h}):min(ih\\,iw*{h}/{w}),scale={w}:{h},setsar=1"
        if city["woven"]:
            graph = (
                f"[0:v]split[p][q];[q]crop={w}:{h}:{x}:{y},format=gbrp[bg];"
                f"[1:v]{fit},format=gbrp,split[v][v2];"
                f"[v][bg]blend=all_mode=multiply[mul];[mul][v2]blend=all_expr='A*0.65+B*0.35',format=rgba[art];"
            )
        else:
            graph = f"[0:v]copy[p];[1:v]{fit},format=rgba[art];"
        graph += f"[2:v]format=gray[m];[art][m]alphamerge[am];[p][am]overlay={x}:{y}:shortest=1,format=yuv420p"
        # the app keeps only the first 3 seconds too
        subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(tmp / "poster.png"),
            "-i", str(tmp / "in.mp4"),
            "-loop", "1", "-i", str(tmp / "mask.png"),
            "-filter_complex", graph, "-t", "3", "-c:v", "libx264", "-crf", "18", str(tmp / "out.mp4"),
        ], check=True)
        name = f"{out}poster.mp4"
        bucket.blob(name).upload_from_filename(tmp / "out.mp4", content_type="video/mp4")
    print(f"On the poster: https://storage.cloud.google.com/{settings.GCS_BUCKET}/{name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("city", choices=list(CITIES))
    ap.add_argument("--only", help="draw just one style (a, b or c)")
    ap.add_argument("--video", help="animate this still (a, b or c)")
    args = ap.parse_args()

    from google.cloud import storage

    from app.config import settings

    city = CITIES[args.city]
    poster = Image.open(POSTERS / f"{args.city}.png")
    bucket = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT).bucket(settings.GCS_BUCKET)
    if args.video:
        asyncio.run(make_video(args, city, poster, settings, bucket))
    else:
        make_stills(args, city, poster, settings, bucket)


if __name__ == "__main__":
    main()
