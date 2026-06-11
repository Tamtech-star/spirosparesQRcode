import os
import sys
from PIL import Image, ImageDraw, ImageFont

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.append(ROOT_DIR)

import qr_generator as qrgen

OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
OUTPUT_IMAGE_PATH = os.path.join(OUTPUT_DIR, "functional_spiro_poster.png")
OUTPUT_HTML_PATH = os.path.join(OUTPUT_DIR, "poster_clickable.html")
PRIMARY_TEMPLATE_PATH = os.path.join(ROOT_DIR, "poster.png")
FALLBACK_TEMPLATE_PATH = os.path.join(ROOT_DIR, "poster_template.png")

WEBSITE_URL_STRING = "https://spirospares.com"
WHATSAPP_NUMBER_STRING = "+254 118 673 848"
TOLL_FREE_NUMBER_STRING = "+254 800722 211"

# Defaults tuned for the provided poster screenshot ratio.
# Override with env vars when your exact artwork has different dimensions:
# QR_LEFT_PCT, QR_TOP_PCT, QR_SIZE_PCT
QR_LEFT_PCT = float(os.environ.get("QR_LEFT_PCT", "0.408"))
QR_TOP_PCT = float(os.environ.get("QR_TOP_PCT", "0.615"))
QR_SIZE_PCT = float(os.environ.get("QR_SIZE_PCT", "0.175"))

# Replace only the two contact lines block.
# Override with env vars if needed.
CONTACT_LEFT_PCT = float(os.environ.get("CONTACT_LEFT_PCT", "0.500"))
CONTACT_TOP_PCT = float(os.environ.get("CONTACT_TOP_PCT", "0.742"))
CONTACT_RIGHT_PCT = float(os.environ.get("CONTACT_RIGHT_PCT", "0.985"))
CONTACT_BOTTOM_PCT = float(os.environ.get("CONTACT_BOTTOM_PCT", "0.845"))


def load_font(size, bold=False):
  candidates = [
    "arialbd.ttf" if bold else "arial.ttf",
    "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
  ]
  for font_name in candidates:
    try:
      return ImageFont.truetype(font_name, size)
    except OSError:
      continue
  return ImageFont.load_default()


def fit_font_for_text(draw, text, max_width, max_height, start_size):
  size = max(12, start_size)
  while size >= 12:
    font = load_font(size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    if text_w <= max_width and text_h <= max_height:
      return font
    size -= 1
  return load_font(12, bold=True)


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

    template_path = PRIMARY_TEMPLATE_PATH if os.path.exists(PRIMARY_TEMPLATE_PATH) else FALLBACK_TEMPLATE_PATH

    if not os.path.exists(template_path):
        print(f"Template not found: {PRIMARY_TEMPLATE_PATH}")
        print(f"Fallback template not found: {FALLBACK_TEMPLATE_PATH}")
        print("Put your exact poster image at project root as: poster.png")
        print("Then run: python src/main.py")
        return

    poster = Image.open(template_path).convert("RGB")
    width, height = poster.size

    qr_size = max(80, int(min(width, height) * QR_SIZE_PCT))
    qr_x = int(width * QR_LEFT_PCT)
    qr_y = int(height * QR_TOP_PCT)

    qr_img = qrgen.generate_secure_qr(WEBSITE_URL_STRING, size=(qr_size, qr_size), border_size=4)
    poster.paste(qr_img, (qr_x, qr_y))

    draw = ImageDraw.Draw(poster)

    # Redraw only the contact lines with updated numbers.
    cx1 = int(width * CONTACT_LEFT_PCT)
    cy1 = int(height * CONTACT_TOP_PCT)
    cx2 = int(width * CONTACT_RIGHT_PCT)
    cy2 = int(height * CONTACT_BOTTOM_PCT)
    draw.rectangle((cx1, cy1, cx2, cy2), fill="white")

    line_1 = f"PLACE YOUR ORDER (WHATSAPP): {WHATSAPP_NUMBER_STRING}"
    line_2 = f"TOLL FREE HELPLINE: {TOLL_FREE_NUMBER_STRING}"

    box_w = cx2 - cx1
    box_h = cy2 - cy1
    per_line_h = max(20, (box_h // 2) - 4)
    start_size = max(14, int(height * 0.050))

    line_1_font = fit_font_for_text(draw, line_1, box_w, per_line_h, start_size)
    line_2_font = fit_font_for_text(draw, line_2, box_w, per_line_h, start_size)

    line_1_y = cy1
    line_2_y = cy1 + per_line_h + 6

    draw.text((cx1, line_1_y), line_1, fill=(16, 18, 24), font=line_1_font)
    draw.text((cx1, line_2_y), line_2, fill=(16, 18, 24), font=line_2_font)

    poster.save(OUTPUT_IMAGE_PATH, quality=96)
    create_clickable_html(os.path.basename(OUTPUT_IMAGE_PATH), WEBSITE_URL_STRING)

    print(f"Poster image written to: {OUTPUT_IMAGE_PATH}")
    print(f"Clickable HTML written to: {OUTPUT_HTML_PATH}")
    print("QR target URL:", WEBSITE_URL_STRING)
    print(f"Template used: {template_path}")
    print(f"QR placement: x={qr_x}, y={qr_y}, size={qr_size}")
    print(f"Updated WhatsApp: {WHATSAPP_NUMBER_STRING}")
    print(f"Updated Toll Free: {TOLL_FREE_NUMBER_STRING}")


if __name__ == "__main__":
    generate_final_poster()