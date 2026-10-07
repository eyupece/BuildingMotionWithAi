import logging
import shutil
import subprocess
import tempfile
import threading

import cv2
import numpy as np  # noqa: F401  (kept for compatibility)


logger = logging.getLogger(__name__)

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def video_lock(name: str) -> threading.Lock:
    """One lock per job step, so the pipeline and a polling request don't both run ffmpeg."""
    with _locks_guard:
        return _locks.setdefault(name, threading.Lock())


def _ffmpeg_exe() -> str | None:
    """Return path to an ffmpeg binary, preferring the imageio-ffmpeg bundle."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    return shutil.which("ffmpeg")


# Length of the clip people record and of the AI video they get back
CLIP_SECONDS = 5.0


def trim_video(input_path: str, duration_s: float) -> str:
    """Trim a video to the first duration_s seconds.

    Uses ffmpeg stream copy (no re-encode) when available; falls back to cv2
    frame-by-frame otherwise.  Returns the path to a new temp .mp4 file.
    The caller is responsible for deleting it.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.close()

    ffmpeg = _ffmpeg_exe()
    if ffmpeg:
        subprocess.run(
            [
                ffmpeg, "-y",
                "-i", input_path,
                "-t", str(duration_s),
                "-c", "copy",
                tmp.name,
            ],
            check=True,
            capture_output=True,
        )
        return tmp.name

    # cv2 fallback (may produce black frames if source codec is H.264)
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp.name, fourcc, fps, (width, height))

    max_frames = int(duration_s * fps)
    frame_count = 0
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    return tmp.name


def compose_videos_side_by_side(original_path: str, generated_path: str) -> str:
    """Compose two videos vertically (9:16) — original on top, generated on bottom.

    Normalises both clips to 1080×960 (letterboxed) then vstacks them to
    produce a 1080×1920 H.264 MP4.  Returns the path to a new temp .mp4 file.
    The caller is responsible for deleting it.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.close()

    ffmpeg = _ffmpeg_exe()
    if ffmpeg:
        filter_complex = (
            "[0:v]scale=1080:960:force_original_aspect_ratio=decrease,"
            "pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=black[top];"
            "[1:v]scale=1080:960:force_original_aspect_ratio=decrease,"
            "pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=black[bot];"
            "[top][bot]vstack=inputs=2[out]"
        )
        cmd = [
            ffmpeg, "-y",
            "-i", original_path,
            "-i", generated_path,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            "-preset", "fast",
            "-movflags", "+faststart",
            "-t", str(CLIP_SECONDS),
            tmp.name,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return tmp.name
        except subprocess.CalledProcessError:
            # libx264 not available — retry with mpeg4
            cmd_fallback = [
                ffmpeg, "-y",
                "-i", original_path,
                "-i", generated_path,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-c:v", "mpeg4",
                "-t", str(CLIP_SECONDS),
                tmp.name,
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True)
            return tmp.name

    raise RuntimeError("ffmpeg not available; cannot compose videos")


_FONTS = "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf"
_W, _H = 1080, 1920


def _font(weight: str, size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype(_FONTS.format(weight), size)
    except OSError:
        return ImageFont.load_default(size)


def _size(path: str) -> tuple[int, int]:
    cap = cv2.VideoCapture(path)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if not w or not h:
        raise RuntimeError(f"Cannot read video size: {path}")
    return w, h


def _fit(w: int, h: int, box_w: int, box_h: int) -> tuple[int, int]:
    r = min(box_w / w, box_h / h)
    # even sizes, libx264 needs them
    return int(w * r) // 2 * 2, int(h * r) // 2 * 2


def _share_layers(main: tuple, pip: tuple, subtitle: str, folder: str) -> dict[str, str]:
    """PNG layers for the share video: shadows under the clips, text on top, rounded masks."""
    from PIL import Image, ImageDraw, ImageFilter

    mx, my, mw, mh = main
    px, py, pw, ph = pip

    under = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(under)
    d.rounded_rectangle((mx, my + 20, mx + mw, my + mh + 20), 36, fill=(0, 0, 0, 110))
    d.rounded_rectangle((px, py + 10, px + pw, py + ph + 10), 24, fill=(0, 0, 0, 110))
    under = under.filter(ImageFilter.GaussianBlur(30))
    ImageDraw.Draw(under).rounded_rectangle((px - 6, py - 6, px + pw + 6, py + ph + 6), 30, fill="white")

    over = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    d.text((_W // 2, 150), "Building Motion with AI", font=_font("Bold", 58), fill="white", anchor="mm")
    if subtitle:
        d.text((_W // 2, 222), subtitle, font=_font("Regular", 40), fill=(255, 255, 255, 210), anchor="mm")
    d.text((px + pw // 2, py + ph + 40), "Ben, gerçekte", font=_font("Bold", 32), fill="white", anchor="mm")

    paths = {}
    for name, img in (
        ("under", under),
        ("over", over),
        ("main_mask", _round_mask(mw, mh, 36)),
        ("pip_mask", _round_mask(pw, ph, 24)),
    ):
        paths[name] = f"{folder}/{name}.png"
        img.save(paths[name])
    return paths


def _round_mask(w: int, h: int, r: int):
    from PIL import Image, ImageDraw

    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), r, fill=255)
    return m


def compose_share_video(original_path: str, generated_path: str, subtitle: str = "") -> str:
    """The video people share: the AI clip big on a blurred copy of itself, their recording
    small in the corner, title on top. 1080x1920 H.264 MP4, CLIP_SECONDS long.

    Falls back to the plain stacked layout if this one fails. Returns a temp .mp4 path
    the caller deletes.
    """
    ffmpeg = _ffmpeg_exe()
    if not ffmpeg:
        raise RuntimeError("ffmpeg not available; cannot compose videos")
    try:
        return _compose_share(ffmpeg, original_path, generated_path, subtitle)
    except Exception:
        logger.exception("Share layout failed, using the stacked one")
        return compose_videos_side_by_side(original_path, generated_path)


def _compose_share(ffmpeg: str, original_path: str, generated_path: str, subtitle: str) -> str:
    mw, mh = _fit(*_size(generated_path), 960, 1300)
    mx, my = (_W - mw) // 2, max(330, (_H - mh) // 2)
    pw, ph = _fit(*_size(original_path), 430, 430)
    px = _W - pw - 50
    py = min(my + mh - ph // 2, _H - ph - 180)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.close()
    with tempfile.TemporaryDirectory() as folder:
        layers = _share_layers((mx, my, mw, mh), (px, py, pw, ph), subtitle, folder)
        graph = (
            "[1:v]split[g1][g2];"
            f"[g1]scale={_W}:{_H}:force_original_aspect_ratio=increase,crop={_W}:{_H},"
            "boxblur=40:2,eq=brightness=-0.12,format=rgba[bg];"
            f"[g2]scale={mw}:{mh},format=rgba[m0];[4:v]format=gray[mm];[m0][mm]alphamerge[main];"
            f"[0:v]scale={pw}:{ph},format=rgba[p0];[5:v]format=gray[pm];[p0][pm]alphamerge[pip];"
            "[bg][2:v]overlay=0:0[a];"
            f"[a][main]overlay={mx}:{my}[b];"
            f"[b][pip]overlay={px}:{py}[c];"
            "[c][3:v]overlay=0:0,format=yuv420p[out]"
        )
        cmd = [
            ffmpeg, "-y",
            "-i", original_path,
            "-i", generated_path,
            "-loop", "1", "-i", layers["under"],
            "-loop", "1", "-i", layers["over"],
            "-loop", "1", "-i", layers["main_mask"],
            "-loop", "1", "-i", layers["pip_mask"],
            "-filter_complex", graph,
            "-map", "[out]",
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-movflags", "+faststart",
            "-t", str(CLIP_SECONDS),
            tmp.name,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    return tmp.name


def _parse_timestamp(timestamp: str) -> float:
    """Parse timestamp string like '0:02' or '1:05' into seconds."""
    parts = timestamp.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


def extract_frame(video_path: str, timestamp: str) -> bytes:
    """Extract a single frame from a video at the given timestamp.

    Args:
        video_path: Local path to the video file.
        timestamp: Timestamp string like "0:02".

    Returns:
        PNG image as bytes.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    try:
        seconds = _parse_timestamp(timestamp)
    except (ValueError, IndexError):
        seconds = 2.5

    frame_number = int(seconds * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    ret, frame = cap.read()
    cap.release()
    if not ret:
        # Browser webm recordings often can't be seeked, and Gemini sometimes
        # picks a timestamp past the end. Read from the start instead and keep
        # the last frame we get up to the target.
        cap = cv2.VideoCapture(video_path)
        frame = None
        for _ in range(max(frame_number, 0) + 1):
            ok, f = cap.read()
            if not ok:
                break
            frame = f
        cap.release()
        if frame is None:
            raise RuntimeError("Could not extract frame from video")

    success, buffer = cv2.imencode(".png", frame)
    if not success:
        raise RuntimeError("Failed to encode frame as PNG")

    return buffer.tobytes()


def extract_storyboard_frames(
    video_path: str, interval_s: float = 0.5
) -> list[tuple[float, bytes]]:
    """Extract frames at regular intervals for storyboard analysis.

    Args:
        video_path: Local path to the video file.
        interval_s: Time between sampled frames in seconds.

    Returns:
        List of (timestamp_seconds, png_bytes) pairs.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    results: list[tuple[float, bytes]] = []
    t = 0.0
    while t <= duration + 0.01:
        frame_number = int(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if ret:
            ok, buf = cv2.imencode(".png", frame)
            if ok:
                results.append((round(t, 2), buf.tobytes()))
        t += interval_s

    cap.release()
    return results
