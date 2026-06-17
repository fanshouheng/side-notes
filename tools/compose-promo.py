from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

root = Path(r'E:\桌面\desk\side-notes')
promo = root / 'assets' / 'promo'
promo.mkdir(parents=True, exist_ok=True)
scene_path = Path(r'C:\Users\Admin\.codex\generated_images\019ed38b-b48c-7bf0-8a2d-1fe2de4bed16\ig_0ecea364e686a090016a32119692fc819a9d7524ff09e29dc5.png')
screenshot_path = promo / 'real-screenshot.png'
hero_path = promo / 'hero.png'

scene = Image.open(scene_path).convert('RGBA')
screenshot = Image.open(screenshot_path).convert('RGBA')
canvas = scene.copy()

# Cover the generated notes panel area with a dark glass panel based on the real app footprint.
panel_box = (1324, 120, 1642, 820)
draw = ImageDraw.Draw(canvas, 'RGBA')
draw.rounded_rectangle(panel_box, radius=12, fill=(8, 10, 14, 232), outline=(255, 255, 255, 38), width=2)

# Place three true UI screenshots as docked note windows.
placements = [
    (1340, 150, 280, 202, 'Today'),
    (1340, 378, 280, 202, 'Ideas'),
    (1340, 606, 280, 172, 'Later'),
]
for x, y, w, h, label in placements:
    note_img = screenshot.resize((w, h), Image.Resampling.LANCZOS)
    shadow = Image.new('RGBA', (w + 22, h + 22), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, 'RGBA')
    sd.rounded_rectangle((11, 11, w + 11, h + 11), radius=8, fill=(0, 0, 0, 125))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(shadow, (x - 11, y - 9))
    canvas.alpha_composite(note_img, (x, y))

# Add subtle product framing without fake feature text.
draw = ImageDraw.Draw(canvas, 'RGBA')
draw.rounded_rectangle(panel_box, radius=12, outline=(125, 211, 252, 72), width=2)

canvas = canvas.convert('RGB')
canvas.save(hero_path, quality=95)
print(hero_path)
