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
        "Paint the person into image 2 as a 17th century Dutch portrait in a black doublet with a large "
        "white lace collar. Keep their own hairstyle, hair color and the smile from the photo. "
        "Warm light from the upper left, visible brushwork. Keep the dark background, the red curtain "
        "on the right and the column. "
        "Waist-up and a little small in the picture, centered, with space on every side. "
        "Both hands fully visible, resting in front of the body in the lower part."
    ),
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
