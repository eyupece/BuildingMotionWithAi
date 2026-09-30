"""DevFest Trabzon 2026: avatar style and location theme."""

AVATAR_STYLE_KEY = 'rembrandt'

AVATAR_STYLE = {
    "name": 'Rembrandt Portrait',
    "description": (
        'Museum-quality 17th-century Dutch Golden Age oil painting in the manner of Rembrandt van Rijn, '
        'as if the person sat for a master painter in Amsterdam. Identity comes first: keep the exact '
        'face shape, eyes, eyebrows, nose, mouth, jawline, hairline, hairstyle, facial hair, skin tone, '
        'moles and natural asymmetry. Do not beautify, idealize, age, de-age or create a generic '
        "Rembrandt face, and keep the person's body proportions. Replace modern clothing with "
        'historically plausible Dutch Baroque dress from about 1620-1680, choosing ONE wardrobe direction'
        ' instead of a default black coat with a large white collar: for example an olive velvet doublet '
        "with a soft falling collar, a burgundy merchant coat over a linen shirt, a scholar's black robe "
        'with a narrow linen collar, a buff leather jerkin, a fur-trimmed wool mantle, a dark bodice with'
        ' a square neckline and linen chemise, or a deep blue satin gown with lace cuffs; restrained '
        'pearl or gold accents only. Classic Rembrandt lighting: warm directional light on one side of '
        'the face with the small triangle of light under the eye on the shadow side, dramatic '
        'chiaroscuro, deep umber shadows, eyes clearly readable. Dark atmospheric brown-black background '
        'with a subtle warm gradient. Palette of raw and burnt umber, burnt sienna, yellow ochre, warm '
        'ivory, muted vermilion and subtle gold. Visible controlled brushwork, subtle impasto on lit '
        'areas, translucent glazing in skin shadows, natural skin texture, slight canvas grain. No '
        'fantasy costumes, crowns or armor, no airbrushed or plastic skin, no modern digital-art or '
        'filtered-photo look, no extra fingers.'
    ),
    "emoji": '🖼️',
}

VIDEO_STYLE = {
    "name": 'Rembrandt Portrait',
    "camera": 'front-facing medium shot',
    "description": (
        'animated 17th-century Dutch Baroque oil painting figure in the manner of Rembrandt, dressed in '
        'period doublet or gown, painted with visible brushstrokes and glazing, clearly a moving oil '
        'painting NOT a real human'
    ),
    "atmosphere": (
        'Rembrandt chiaroscuro lighting, warm golden highlights against deep umber shadows, visible oil '
        'brushwork and canvas texture, museum painting that has come to life'
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
