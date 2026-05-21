import random
from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

_COLOR_LIGHT_BLUE = (179, 213, 240)
_COLOR_LIGHT_GREEN = (179, 240, 197)
_COLOR_LIGHT_YELLOW = (240, 219, 179)
_COLOR_LIGHT_PURPLE = (225, 179, 240)
_COLOR_LIGHT_RED = (240, 179, 179)
_COLOR_LIGHT_CYAN = (179, 237, 240)

PASTEL_COLORS = [
    _COLOR_LIGHT_BLUE,
    _COLOR_LIGHT_GREEN,
    _COLOR_LIGHT_YELLOW,
    _COLOR_LIGHT_PURPLE,
    _COLOR_LIGHT_RED,
    _COLOR_LIGHT_CYAN,
]

_DEJAVU_FONT_NAME = "DejaVuSans-Bold.ttf"

_FONT_PATHS = [
    f"/usr/share/fonts/truetype/dejavu/{_DEJAVU_FONT_NAME}",
    f"/usr/share/fonts/dejavu/{_DEJAVU_FONT_NAME}",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = AVATAR_SIZE // 2
AVATAR_LETTER_COLOR = (255, 255, 255)


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default(size=size)


def generate_avatar(name: str) -> ContentFile:
    color = random.choice(PASTEL_COLORS)
    img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=color)
    draw = ImageDraw.Draw(img)
    letter = name[0].upper() if name else "?"
    font = _load_font(AVATAR_FONT_SIZE)
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), letter, fill=AVATAR_LETTER_COLOR, font=font)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"avatar_{uuid4()}.png")
