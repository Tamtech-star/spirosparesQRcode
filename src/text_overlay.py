from PIL import ImageDraw, ImageFont

def draw_dynamic_texts(draw, texts_and_coords, font_path, font_size=32, fill="blue"):
    """Draws a list of texts at specified coordinates with a given font."""
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font not found at {font_path}. Falling back to default system font.")
        font = ImageFont.load_default()

    for text_string, coords in texts_and_coords:
        draw.text(coords, text_string, fill=fill, font=font)