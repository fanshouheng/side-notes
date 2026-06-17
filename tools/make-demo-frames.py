from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(r'E:\桌面\desk\side-notes')
PROMO = ROOT / 'assets' / 'promo'
frames = PROMO / 'frames'
frames.mkdir(parents=True, exist_ok=True)
hero = Image.open(PROMO / 'hero.png').convert('RGBA')
shot = Image.open(PROMO / 'real-screenshot.png').convert('RGBA').resize((320, 230), Image.Resampling.LANCZOS)

for i in range(90):
    t = i / 89
    frame = hero.copy()
    overlay = Image.new('RGBA', frame.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay, 'RGBA')
    x = int(1500 - min(1, t * 2.2) * 420)
    y = 290 + int(16 * __import__('math').sin(t * 6.283))
    shadow = Image.new('RGBA', (360, 270), (0,0,0,0))
    sd = ImageDraw.Draw(shadow, 'RGBA')
    sd.rounded_rectangle((20,20,340,250), radius=8, fill=(0,0,0,130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    overlay.alpha_composite(shadow, (x-20, y-20))
    crop_y = int(max(0, min(34, (t - 0.35) * 80)))
    moved = shot.crop((0, crop_y, 320, 230)).resize((320, 230), Image.Resampling.LANCZOS)
    overlay.alpha_composite(moved, (x, y))
    frame = Image.alpha_composite(frame, overlay)
    frame.convert('RGB').save(frames / f'frame_{i:03d}.png', quality=92)
print(frames)
