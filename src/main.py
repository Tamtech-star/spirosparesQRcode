import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.append(ROOT_DIR)

import qr_generator as qrgen

OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
OUTPUT_IMAGE_PATH = os.path.join(OUTPUT_DIR, "functional_spiro_poster.png")
OUTPUT_HTML_PATH = os.path.join(OUTPUT_DIR, "poster_clickable.html")

WEBSITE_URL_STRING = "https://spirospares.com"
WHATSAPP_NUMBER_CALLOUT = "+254 118 673848"
TOLL_FREE_NUMBER_CALLOUT = "+254 733-959-383"


def load_font(size, bold=False):
    """Load a bundled system font where possible, otherwise use PIL default."""
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_hex_pattern(draw, width, height, color=(210, 214, 220), spacing=95):
    """Draw light background hex outlines to resemble the reference artwork."""
    r = 28
    for y in range(80, height - 100, int(spacing * 0.9)):
        for x in range(50, width - 50, spacing):
            if (x // spacing + y // spacing) % 2 == 0:
                continue
            pts = [
                (x - r, y),
                (x - r // 2, y - int(r * 0.86)),
                (x + r // 2, y - int(r * 0.86)),
                (x + r, y),
                (x + r // 2, y + int(r * 0.86)),
                (x - r // 2, y + int(r * 0.86)),
                (x - r, y),
            ]
            draw.line(pts, fill=color, width=2)


def draw_bike_hint(draw, origin_x, origin_y, facing="right"):
    """Stylized bike/rider hint so the poster keeps the same visual rhythm."""
    wheel_color = (35, 35, 35)
    accent = (103, 203, 47)
    draw.ellipse((origin_x, origin_y, origin_x + 145, origin_y + 145), outline=wheel_color, width=8)
    draw.ellipse((origin_x + 230, origin_y, origin_x + 375, origin_y + 145), outline=wheel_color, width=8)

    if facing == "right":
        p1, p2, p3 = (origin_x + 72, origin_y + 75), (origin_x + 210, origin_y + 48), (origin_x + 280, origin_y + 75)
        rider_center = (origin_x + 205, origin_y - 35)
    else:
        p1, p2, p3 = (origin_x + 305, origin_y + 75), (origin_x + 165, origin_y + 48), (origin_x + 95, origin_y + 75)
        rider_center = (origin_x + 170, origin_y - 35)

    draw.line((p1, p2, p3, p1), fill=(45, 45, 45), width=8)
    draw.line((p2, (p2[0], p2[1] + 55)), fill=(45, 45, 45), width=8)
    draw.rounded_rectangle((p2[0] - 50, p2[1] + 18, p2[0] + 55, p2[1] + 64), radius=10, fill=accent)
    draw.ellipse((rider_center[0] - 22, rider_center[1] - 22, rider_center[0] + 22, rider_center[1] + 22), fill=(20, 20, 20))
    draw.line((rider_center[0], rider_center[1] + 20, p2[0] + 4, p2[1] + 12), fill=(20, 20, 20), width=11)


def create_clickable_html(image_filename, target_url):
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Spiro Spares Poster</title>
  <style>
    body {{ margin: 0; background: #f5f7fb; display: grid; place-items: center; min-height: 100vh; }}
    a {{ display: inline-block; max-width: min(94vw, 1200px); }}
    img {{ width: 100%; height: auto; border-radius: 14px; box-shadow: 0 22px 60px rgba(0, 0, 0, .16); }}
  </style>
</head>
<body>
  <a href=\"{target_url}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"Open Spiro Spares website\">
    <img src=\"{image_filename}\" alt=\"Spiro Spares QR order poster\" />
  </a>
</body>
</html>
"""
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def generate_final_poster():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width, height = 1600, 1200
    poster = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(poster)

    draw_hex_pattern(draw, width, height)

    blue = (19, 57, 181)
    green = (93, 198, 38)
    dark = (20, 24, 33)

    title_font = load_font(74, bold=True)
    mid_font = load_font(42, bold=True)
    text_font = load_font(36, bold=False)
    small_font = load_font(27, bold=False)

    draw.text((80, 40), "spiro", font=title_font, fill=blue)
    draw.text((84, 124), "spares", font=mid_font, fill=blue)
    draw.rounded_rectangle((78, 180, 365, 236), radius=25, fill=(30, 136, 229))
    draw.text((94, 192), "Powered by Tamtech", font=load_font(30, bold=True), fill="white")

    draw.text((540, 70), "ORDER ONLINE", font=load_font(62, bold=True), fill=blue)
    draw.text((540, 140), "NOW!", font=load_font(108, bold=True), fill=green)

    badge_x = width - 280
    draw.rounded_rectangle((badge_x, 24, badge_x + 214, 278), radius=28, fill=(99, 53, 215))
    today = datetime.now().strftime("%b %dTH\n%Y\n4:30PM").upper()
    draw.multiline_text((badge_x + 30, 62), today, font=load_font(44, bold=True), fill="white", spacing=8, align="center")

    laptop = (505, 255, 1130, 688)
    draw.rounded_rectangle(laptop, radius=26, fill=(12, 35, 92), outline=(10, 10, 10), width=5)
    draw.rectangle((laptop[0] + 26, laptop[1] + 42, laptop[2] - 26, laptop[3] - 28), fill=(38, 92, 210))
    draw.rounded_rectangle((laptop[0] + 40, laptop[1] + 55, laptop[0] + 180, laptop[1] + 100), radius=20, fill=green)
    draw.text((laptop[0] + 58, laptop[1] + 64), "SHOP NOW", font=load_font(24, bold=True), fill="white")
    draw.text((laptop[0] + 56, laptop[1] + 130), "GENUINE SPARES", font=load_font(54, bold=True), fill="white")
    draw.text((laptop[0] + 56, laptop[1] + 205), "BUILT FOR", font=load_font(58, bold=True), fill=green)
    draw.text((laptop[0] + 56, laptop[1] + 280), "PERFORMANCE", font=load_font(58, bold=True), fill=green)

    draw_bike_hint(draw, 95, 570, facing="right")
    draw_bike_hint(draw, 1115, 570, facing="left")

    qr_size = 260
    qr_x, qr_y = 570, 760
    qr_img = qrgen.generate_secure_qr(WEBSITE_URL_STRING, size=(qr_size, qr_size), border_size=4)
    poster.paste(qr_img, (qr_x, qr_y))

    draw.text((qr_x + qr_size + 34, qr_y + 40), "SCAN QR CODE", font=mid_font, fill=dark)
    draw.text((qr_x + qr_size + 34, qr_y + 95), "TO VISIT WEBSITE", font=mid_font, fill=dark)

    draw.text((qr_x + qr_size + 34, qr_y + 170), f"PLACE YOUR ORDER (WHATSAPP): {WHATSAPP_NUMBER_CALLOUT}", font=text_font, fill=dark)
    draw.text((qr_x + qr_size + 34, qr_y + 225), f"TOLL FREE HELPLINE: {TOLL_FREE_NUMBER_CALLOUT}", font=text_font, fill=dark)
    draw.text((width // 2 - 145, 1095), WEBSITE_URL_STRING, font=load_font(44, bold=True), fill=blue)

    pills = [
        (90, 1128, 420, 1182, "GENUINE SPARES"),
        (455, 1128, 785, 1182, "EASY ORDERING"),
        (820, 1128, 1160, 1182, "RELIABLE DELIVERY"),
        (1195, 1128, 1540, 1182, "POWERED BY TAMTECH"),
    ]
    for x1, y1, x2, y2, label in pills:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=23, fill=blue)
        tw = draw.textlength(label, font=load_font(30, bold=True))
        draw.text((x1 + ((x2 - x1) - tw) / 2, y1 + 10), label, font=load_font(30, bold=True), fill="white")

    poster.save(OUTPUT_IMAGE_PATH, quality=96)
    create_clickable_html(os.path.basename(OUTPUT_IMAGE_PATH), WEBSITE_URL_STRING)

    print(f"Poster image written to: {OUTPUT_IMAGE_PATH}")
    print(f"Clickable HTML written to: {OUTPUT_HTML_PATH}")
    print("QR target URL:", WEBSITE_URL_STRING)


if __name__ == "__main__":
    generate_final_poster()