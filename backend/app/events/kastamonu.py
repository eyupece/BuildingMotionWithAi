"""DevFest Kastamonu 2026.

The poster: a Kastamonu weaver at her loom. The poster kit stitches you into
the cloth on that loom, and the Kastamonu street is a world for the other styles.
"""

POSTER_KEY = 'kastamonu-afis'

POSTER = {
    "image": "kastamonu.png",
    # x, y, w, h of the empty cloth on the loom
    "slot": (468, 482, 232, 338),
    "woven": True,
    "art": "a portrait woven into a cream kilim cloth on a loom",
    "portrait": (
        "Stitch the person onto the cream linen of image 2 as cross-stitch embroidery in rust red, "
        "indigo blue, mustard and moss green thread. "
        # hands have to be in the picture from the start, or Veo makes up extra ones
        "Waist-up, filling the width of the picture, centered, head in the upper third. "
        "Both hands fully visible, resting in front of the body in the lower part."
    ),
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
