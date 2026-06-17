from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PROMO_DIR = ROOT / "assets" / "promo"
SCREENSHOT_PATH = PROMO_DIR / "real-screenshot.png"
HERO_PATH = PROMO_DIR / "hero.png"


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def rounded_shadow(size, radius, blur=24, opacity=120):
    shadow = Image.new("RGBA", (size[0] + blur * 2, size[1] + blur * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow, "RGBA")
    draw.rounded_rectangle((blur, blur, blur + size[0], blur + size[1]), radius=radius, fill=(0, 0, 0, opacity))
    return shadow.filter(ImageFilter.GaussianBlur(blur // 2))


def make_hero():
    screenshot = Image.open(SCREENSHOT_PATH).convert("RGBA")
    canvas = Image.new("RGBA", (1600, 900), (14, 18, 26, 255))
    draw = ImageDraw.Draw(canvas, "RGBA")

    for x in range(0, 1600, 40):
        alpha = int(22 * (1 - x / 1800))
        draw.line((x, 0, x - 320, 900), fill=(255, 255, 255, alpha), width=1)

    draw.rounded_rectangle((120, 96, 1120, 760), radius=22, fill=(28, 34, 46, 255), outline=(255, 255, 255, 26), width=2)
    draw.rounded_rectangle((150, 132, 1090, 704), radius=12, fill=(10, 14, 22, 255))
    draw.rounded_rectangle((180, 174, 820, 620), radius=12, fill=(20, 26, 36, 255))

    code_font = font(22)
    code_lines = [
        "function captureIdeas() {",
        "  notes.dockTo('right')",
        "  notes.keepVisible(true)",
        "  return focus.withoutContextSwitching()",
        "}",
    ]
    y = 230
    for i, line in enumerate(code_lines, 1):
        draw.text((230, y), f"{i}", fill=(104, 119, 141, 255), font=code_font)
        draw.text((280, y), line, fill=(191, 219, 254, 235), font=code_font)
        y += 54

    panel_shadow = rounded_shadow((360, 650), 18, opacity=150)
    canvas.alpha_composite(panel_shadow, (1000, 96))
    draw.rounded_rectangle((1040, 124, 1400, 774), radius=18, fill=(7, 10, 16, 245), outline=(125, 211, 252, 150), width=2)
    draw.text((1084, 166), "Side Notes", fill=(255, 255, 255, 245), font=font(26, True))

    note = screenshot.resize((320, 230), Image.Resampling.LANCZOS)
    for idx, y in enumerate((226, 482)):
        window_shadow = rounded_shadow((320, 230), 8, blur=18, opacity=125)
        canvas.alpha_composite(window_shadow, (1055, y - 16))
        canvas.alpha_composite(note, (1068, y))
        if idx == 1:
            overlay = Image.new("RGBA", note.size, (0, 0, 0, 78))
            canvas.alpha_composite(overlay, (1068, y))

    draw.text((120, 790), "Side Notes", fill=(255, 255, 255, 255), font=font(54, True))
    draw.text((122, 850), "Dockable desktop notes that stay beside your work.", fill=(203, 213, 225, 240), font=font(26))

    canvas.convert("RGB").save(HERO_PATH, quality=95)


if __name__ == "__main__":
    make_hero()
    print(HERO_PATH)
