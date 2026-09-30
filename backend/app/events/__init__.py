"""DevFest themes: one location per event."""

from pathlib import Path

from app.events import kastamonu, trabzon

EVENTS = {
    "kastamonu": kastamonu,
    "trabzon": trabzon,
}

_SCENES = Path(__file__).parent / "scenes"


def scene_image(location_key: str) -> tuple[bytes, str] | None:
    """Photo of the real place, if one is in events/scenes/<key>.jpg|png.

    Veo only knows the city from the prompt text otherwise, so it makes up a
    generic old town. Passing the photo as a reference keeps the landmarks.
    """
    for ext, mime in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("png", "image/png")):
        path = _SCENES / f"{location_key}.{ext}"
        if path.exists():
            return path.read_bytes(), mime
    return None
