"""DevFest Trabzon 2026.

The poster: a gallery of old master portraits with an empty gold frame in the
middle. The poster kit paints you into that frame, and the Trabzon hills are a
world for the other styles.
"""

POSTER_KEY = 'trabzon-afis'

POSTER = {
    "image": "trabzon.png",
    # x, y, w, h of the canvas inside the gold frame
    "slot": (388, 353, 350, 494),
    "woven": False,
    "art": "an old master oil painting",
    "portrait": (
        "Paint the person into image 2 as a 17th century Dutch portrait wearing {outfit}. "
        "Cut the clothes for the person in the photo: menswear for a man, a gown for a woman. "
        "Keep their own hairstyle, hair color and the smile from the photo. "
        "Warm light from the upper left, visible brushwork. Keep the dark background, the red curtain "
        "on the right and the column. "
        "Waist-up, filling the width of the picture, centered, head in the upper third. "
        "Both hands fully visible, resting in front of the body in the lower part."
    ),
    # one is picked at random per person, so the gallery isn't all the same coat.
    # Colors and collars only; the model picks the cut from the photo.
    "outfits": [
        "black with a large white lace collar and lace cuffs",
        "a burgundy velvet coat with a soft falling white linen collar",
        "a dark fur-trimmed wool cloak over a white linen collar",
        "olive green satin with a narrow white collar and lace cuffs",
        "deep blue silk with a pleated white ruff",
        "brown leather over a white linen shirt with a wide collar",
    ],
}

LOCATION_KEY = 'trabzon'

# Style-neutral like Kastamonu: the avatar style decides how it is drawn.
LOCATION = {
    "name": 'Trabzon',
    "match_style": True,
    "camera": 'medium-wide shot at eye level, full body visible, character in the foreground with the city clearly behind',
    "background": (
        'on a hillside terrace above Trabzon, Turkey, standing in the foreground: bright green terraced '
        'tea gardens roll down toward the Black Sea harbor with fishing boats, the Byzantine Hagia Sophia '
        'of Trabzon with its stone dome near the shore, old city walls climbing the ridge, and far away '
        'the Sumela Monastery clinging to a steep forested cliff, soft Black Sea mist drifting over the '
        'hills, fresh daylight'
    ),
}
