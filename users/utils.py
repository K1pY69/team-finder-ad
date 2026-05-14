import random
from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

PASTEL_COLORS = [
    (179, 213, 240),
    (179, 240, 197),
    (240, 219, 179),
    (225, 179, 240),
    (240, 179, 179),
    (179, 237, 240),
]

_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def generate_avatar(name: str) -> ContentFile:
    color = random.choice(PASTEL_COLORS)
    img = Image.new("RGB", (200, 200), color=color)
    draw = ImageDraw.Draw(img)
    letter = name[0].upper() if name else "?"
    font = _load_font(100)
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (200 - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (200 - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), letter, fill=(255, 255, 255), font=font)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"avatar_{uuid4()}.png")
