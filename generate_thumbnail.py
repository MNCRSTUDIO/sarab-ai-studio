import sys, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def is_devanagari(text):
    # Check if text contains Devanagari Unicode range
    return bool(re.search(r'[\u0900-\u097F]', text))

def get_best_font(is_hindi=False, size=85):
    # Devanagari aur English font paths check
    hindi_font_paths = [
        "/data/data/com.termux/files/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.otf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/NotoSansDevanagari-Bold.ttf",
        "/system/fonts/NotoSansDevanagari-Bold.ttf",
        "/system/fonts/Roboto-Bold.ttf"
    ]
    eng_font_paths = [
        "/system/fonts/Roboto-Bold.ttf",
        "/system/fonts/DroidSans-Bold.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
    ]
    paths = hindi_font_paths if is_hindi else eng_font_paths
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def create_ai_thumbnail(base_image_path, prompt_text, output_path="static/latest_thumbnail.jpg"):
    canvas_w, canvas_h = 1080, 1920
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Background setup: Blurred foreground
    if os.path.exists(base_image_path):
        img = Image.open(base_image_path).convert("RGBA")
        bg = img.resize((canvas_w, canvas_h)).filter(ImageFilter.GaussianBlur(18))
        img.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        offset_x = (canvas_w - img.width) // 2
        offset_y = (canvas_h - img.height) // 2
        bg.paste(img, (offset_x, offset_y), img if "A" in img.getbands() else None)
    else:
        bg = Image.new("RGBA", (canvas_w, canvas_h), (11, 15, 25, 255))
        
    draw = ImageDraw.Draw(bg)
    is_hindi = is_devanagari(prompt_text)
    font = get_best_font(is_hindi=is_hindi, size=85)
    
    # Trend-based Hook Text Selection
    words = prompt_text.strip().split()
    if is_hindi:
        top_hook = "🔥 नया अपडेट!" if not words else " ".join(words[:4])
        bottom_hook = "⚡ अभी देखें!" if len(words) <= 4 else " ".join(words[4:8])
    else:
        top_hook = "🔥 DON'T MISS!" if not words else " ".join(words[:4]).upper()
        bottom_hook = "⚡ WATCH NOW!" if len(words) <= 4 else " ".join(words[4:8]).upper()

    # Top Badge: High-contrast Vibrant Yellow on Dark Outline
    draw.rectangle([40, 180, 1040, 360], fill=(10, 10, 15, 220), outline=(250, 204, 21, 255), width=7)
    draw.text((70, 230), top_hook[:24], fill=(255, 230, 0, 255), font=font)

    # Bottom Badge: Trending Neon Red with White Border
    draw.rectangle([40, 1560, 1040, 1740], fill=(225, 29, 72, 235), outline=(255, 255, 255, 255), width=7)
    draw.text((70, 1610), bottom_hook[:24], fill=(255, 255, 255, 255), font=font)

    bg.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"[AI Thumbnail Generated] Language: {'Hindi' if is_hindi else 'English'} -> {output_path}")

if __name__ == "__main__":
    img_in = sys.argv[1] if len(sys.argv) > 1 else "logo.png"
    text_in = sys.argv[2] if len(sys.argv) > 2 else "SARAB AI STUDIO"
    out_file = sys.argv[3] if len(sys.argv) > 3 else "static/latest_thumbnail.jpg"
    create_ai_thumbnail(img_in, text_in, out_file)
