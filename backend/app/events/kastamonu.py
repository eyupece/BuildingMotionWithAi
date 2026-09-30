"""DevFest Kastamonu 2026.

The poster idea: a Kastamonu weaver weaves the speaker into a kilim, with
Google colored threads on the loom. The "Dokuma" kit turns you into that
kilim figure, and the Kastamonu street is a world for the other styles.
"""

AVATAR_STYLE_KEY = 'kastamonu-dokuma'

AVATAR_STYLE = {
    "name": 'Kastamonu Dokuma',
    "description": (
        'Hand-woven Anatolian kilim tapestry, like a traditional Kastamonu flat-weave. The whole figure '
        'is made of visible woven wool threads on a loom grid: every shape is built from small stepped '
        'warp-and-weft blocks, so edges are slightly stair-stepped like hand weaving, with real wool '
        'texture and soft fibre fuzz. Keep the face clearly recognizable: face shape, glasses, beard and '
        'hairstyle are woven in careful detail. Their own clothes are re-woven in their real colors. '
        'Palette of natural root dyes: madder red, indigo blue, walnut brown, saffron yellow, olive green '
        'and undyed cream wool, with a few bright Google blue, red, yellow and green threads as accents. '
        'Small traditional kilim motifs (elibelinde, ram horn, eight-pointed star) are woven into the '
        'clothing. The figure stands on its own like a woven character, not a rectangular rug, on a plain '
        'cream background. Textile artwork, not a 3D render, not a photo.'
    ),
    "emoji": '🧶',
}

VIDEO_STYLE = {
    "name": 'Kastamonu Dokuma',
    "camera": 'front-facing medium shot',
    "description": (
        'figure woven from colorful wool threads, a living Anatolian kilim tapestry with stair-stepped '
        'woven edges, clearly a textile artwork and NOT a real human'
    ),
    "atmosphere": (
        'hand-woven wool texture with visible warp and weft threads, madder red, indigo, saffron and cream '
        'root-dye colors with bright Google blue, red, yellow and green thread accents, the woven body '
        'bends and moves freely like a living character, warm golden window light, like a vintage '
        'illustrated poster'
    ),
}

# Only used with the Dokuma style: the weaving room from the poster
KIT_LOCATION_KEY = 'kastamonu-tezgah'

KIT_LOCATION = {
    "name": 'Dokuma Tezgahı',
    # The figure used to sit inside the kilim on the loom, and Veo moved the loom
    # instead of the person. It now stands in front of the loom and does the move.
    "camera": 'medium-wide shot at eye level, full body visible, the woven character in the foreground and the loom behind',
    "background": (
        'standing on the wooden floor in front of a large wooden hand loom in the weaving room of an old '
        'Ottoman-era Kastamonu mansion, the character is the woven figure that has just come to life from '
        'the half-finished kilim on the loom behind it: dark carved walnut wall panels and ceiling beams, '
        'a small wooden-framed window showing the hillside of red-roofed Kastamonu houses and the castle, '
        'threads in Google blue, red, yellow and green hanging from the top beam of the loom, balls of '
        'blue, red, yellow and green wool on a small wooden bench, a patterned kilim rug on the floor, '
        'copper coffee pots on a side table, no modern objects, warm golden late-afternoon light. The loom '
        'and the room stay completely still; only the character moves'
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
