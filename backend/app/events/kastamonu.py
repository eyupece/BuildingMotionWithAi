"""DevFest Kastamonu 2026.

The poster: a Kastamonu weaver at her loom. The poster kit draws you into
the cloth on that loom, and the Kastamonu street is a world for the other styles.
"""

POSTER_KEY = 'kastamonu-afis'

POSTER = {
    "image": "kastamonu.png",
    # x, y, w, h of the empty cloth on the loom
    "slot": (468, 482, 232, 338),
    "woven": True,
    # the cloth is small in the poster, so the video starts close on it and pulls back
    "zoom": 2.5,
    "art": "a warm engraving-style illustration woven into a cream kilim cloth on a loom",
    # Cross-stitch didn't survive Veo's motion, so the poster's own engraving look instead.
    # Always upright and facing forward, people often record leaning back or from below.
    "portrait": (
        "Draw the person onto the cream cloth of image 2 as a picture woven into the kilim, in the same "
        "style as a warm old storybook engraving: fine dark brown ink lines with cross-hatching, soft sepia "
        "shading and muted rust red, indigo blue, mustard and moss green, the cloth texture showing through. "
        "Draw them sitting upright and facing the viewer, even if the photo is tilted, taken from below "
        "or they are lying down. "
        # hands have to be in the picture from the start, or Veo makes up extra ones
        "Waist-up, filling the width of the picture, centered, head in the upper third. "
        "Both hands fully visible, resting in front of the body in the lower part."
    ),
    # Veo used to keep the resting hands and grow a third arm, pushed toward the camera
    "video_rules": (
        "A hand that rises is one of the two resting hands and leaves its place, so the person never "
        "has more than two hands. The hands stay at the same distance as the body, never come toward "
        "the camera and never cover the face. Every moving part keeps the same ink lines and color "
        "wash as the rest of the drawing."
    ),
    # how much of the drawing shows over the cloth texture, less washed it out
    "keep": 0.6,
}

LOCATION_KEY = 'kastamonu'

# No rendering style here on purpose: the avatar style (Pixel Hero, 3D Figurine...)
# decides how the scene is drawn, the location only says where it is.
LOCATION = {
    "name": 'Kastamonu',
    "match_style": True,
    "camera": 'medium-wide shot at eye level, full body visible, character in the foreground with the city clearly behind',
    "background": (
        'on a cobblestone street in the old town of Kastamonu, Turkey, standing in the foreground at '
        'street level: two-storey Ottoman timber-framed mansions with white walls, dark wooden beams, '
        'carved bay windows and red tile roofs line the street, the medieval Kastamonu Castle with its '
        'stone towers crowns the rocky hill behind, the slender old Clock Tower rises on the opposite '
        'slope, colorful hand-woven Kastamonu textiles hang from a wooden balcony, forested Ilgaz '
        'mountains in the distance, warm late-afternoon sunlight, lively and welcoming'
    ),
}
