"""DevFest Kastamonu 2026: avatar style and location theme."""

AVATAR_STYLE_KEY = 'kastamonu-gravur'

AVATAR_STYLE = {
    "name": 'Kastamonu Engraving',
    "description": (
        'Antique hand-engraved book illustration from 19th-century Anatolia, like a plate from an old '
        'travel book or a vintage Ottoman-era postcard. Fine cross-hatched ink linework and copperplate '
        'engraving detail on aged, slightly worn cream paper with subtle foxing and grain. Warm muted '
        'palette of sepia, walnut brown, antique bronze and faded sage green, with only small accents of '
        'madder red and indigo taken from traditional Kastamonu hand-woven textiles. The person wears '
        'their own clothing re-drawn in engraved line, with a small kilim-pattern border detail on the '
        'collar or cuffs. Plain aged-paper background with delicate Ottoman floral corner ornaments '
        '(tulips, carnations, rumi scrolls). Soft warm window light, calm nostalgic mood. Flat printed '
        'illustration only: no photorealism, no 3D rendering, no glossy or saturated modern colors.'
    ),
    "emoji": '🪡',
}

VIDEO_STYLE = {
    "name": 'Kastamonu Engraving',
    "camera": 'front-facing medium shot',
    "description": (
        'animated antique engraving illustration character drawn in fine sepia cross-hatched ink lines on'
        ' aged paper, like a figure from a 19th-century Anatolian book plate, clearly an illustration NOT'
        ' a real human'
    ),
    "atmosphere": (
        'vintage copperplate engraving look, warm sepia, brown, bronze and faded sage green tones, subtle'
        ' worn paper grain, traditional Anatolian and Ottoman ornament details, hand-drawn line animation'
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
