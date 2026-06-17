from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PROMO = ROOT / "promo"

FONT_REG = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_LIGHT = "C:/Windows/Fonts/msyhl.ttc"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, value, size, fill, weight="regular", anchor=None, spacing=6):
    path = {"regular": FONT_REG, "bold": FONT_BOLD, "light": FONT_LIGHT, "mono": FONT_MONO}.get(weight, FONT_REG)
    draw.multiline_text(xy, value, font=font(path, size), fill=fill, anchor=anchor, spacing=spacing)


def text_width(value, size, weight="regular"):
    path = {"regular": FONT_REG, "bold": FONT_BOLD, "light": FONT_LIGHT, "mono": FONT_MONO}.get(weight, FONT_REG)
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), value, font=font(path, size))
    return bbox[2] - bbox[0]


def fit_text(draw, value, max_width, size, fill, xy, weight="regular"):
    words = value.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, size, weight) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    text(draw, xy, "\n".join(lines), size, fill, weight=weight, spacing=10)


def add_noise(img, alpha=18):
    noise = Image.effect_noise(img.size, 42).convert("L")
    noise = Image.merge("RGBA", [noise, noise, noise, noise.point(lambda p: alpha)])
    return Image.alpha_composite(img.convert("RGBA"), noise)


def draw_note_window(draw, x, y, w, h, title, todos, collapsed=False):
    tab_w = 54
    rounded_rect(draw, (x, y, x + w, y + h), 12, (8, 10, 12, 190), outline=(255, 255, 255, 34), width=1)
    rounded_rect(draw, (x, y, x + tab_w, y + h), 12, (0, 0, 0, 170))
    draw.rectangle((x + tab_w - 8, y, x + tab_w, y + h), fill=(0, 0, 0, 170))

    tab_text = title[:4]
    for i, ch in enumerate(tab_text):
        text(draw, (x + 19, y + 22 + i * 34), ch, 22, (255, 255, 255, 210), weight="bold")

    if collapsed:
        return

    text(draw, (x + tab_w + 24, y + 22), title, 23, (255, 255, 255, 238), weight="bold")
    text(draw, (x + tab_w + 118, y + 20), "Todo | Done", 22, (255, 255, 255, 190), weight="bold")
    yy = y + 66
    for i, todo in enumerate(todos, 1):
        if yy + 30 > y + h - 10:
            break
        color = (255, 255, 255, 225) if i != 2 else (130, 247, 209, 240)
        text(draw, (x + tab_w + 24, yy), f"{i}. {todo}", 21, color)
        yy += 42


def draw_right_stack(draw, left, top, scale=1.0):
    w = int(360 * scale)
    gap = int(20 * scale)
    draw_note_window(draw, left, top, w, int(180 * scale), "工作", ["今天必须处理的三件事", "写完说明文档", "发一个版本"], False)
    draw_note_window(draw, left, top + int(180 * scale) + gap, w, int(142 * scale), "灵感", ["突然想到的功能点", "下次再做的小优化"], False)
    draw_note_window(draw, left + w - int(54 * scale), top + int(342 * scale) + gap * 2, w, int(120 * scale), "稍后", [], True)


def draw_icon():
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded_rect(d, (92, 92, 932, 932), 208, (9, 11, 14, 255))
    d.rounded_rectangle((92, 92, 932, 932), 208, outline=(255, 255, 255, 36), width=5)

    colors = [(130, 247, 209, 255), (255, 213, 92, 255), (255, 255, 255, 235)]
    ys = [238, 392, 546]
    for idx, y in enumerate(ys):
        rounded_rect(d, (262, y, 746, y + 120), 30, (255, 255, 255, 28), outline=(255, 255, 255, 70), width=3)
        rounded_rect(d, (746, y, 822, y + 120), 28, colors[idx])
        d.rectangle((746, y + 18, 770, y + 102), fill=colors[idx])
        d.line((310, y + 42, 662, y + 42), fill=(255, 255, 255, 178), width=16)
        d.line((310, y + 78, 578, y + 78), fill=(255, 255, 255, 92), width=12)

    rounded_rect(d, (228, 704, 820, 758), 27, (130, 247, 209, 255))
    text(d, (512, 831), "Side Notes", 62, (255, 255, 255, 218), weight="bold", anchor="mm")
    img.save(ASSETS / "icon.png")
    img.resize((256, 256), Image.Resampling.LANCZOS).save(ASSETS / "icon-256.png")
    img.resize((64, 64), Image.Resampling.LANCZOS).save(ASSETS / "tray.png")
    img.save(ASSETS / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])


def draw_github_hero():
    img = Image.new("RGBA", (1600, 900), (8, 10, 13, 255))
    d = ImageDraw.Draw(img)

    for i in range(0, 1600, 80):
        d.line((i, 0, i, 900), fill=(255, 255, 255, 10), width=1)
    for j in range(0, 900, 80):
        d.line((0, j, 1600, j), fill=(255, 255, 255, 8), width=1)

    rounded_rect(d, (90, 88, 132, 132), 10, (130, 247, 209, 255))
    text(d, (154, 92), "SIDE NOTES", 30, (255, 255, 255, 230), weight="mono")
    text(d, (94, 214), "把零散任务\n贴在屏幕边上", 92, (255, 255, 255, 246), weight="light", spacing=18)
    text(d, (98, 468), "一列自动吸附的桌面便签\n缩进去，只露出标题；点一下，再展开。", 34, (255, 255, 255, 188), spacing=12)

    pills = ["多便签窗口", "右侧吸附", "一键缩进", "本地保存"]
    x = 98
    for pill in pills:
        tw = text_width(pill, 24, "bold")
        rounded_rect(d, (x, 664, x + tw + 42, 718), 8, (255, 255, 255, 34), outline=(255, 255, 255, 72))
        text(d, (x + 21, 675), pill, 23, (255, 255, 255, 228), weight="bold")
        x += tw + 58

    d.rectangle((1514, 0, 1600, 900), fill=(130, 247, 209, 255))
    draw_right_stack(d, 920, 150, 1.18)
    img = add_noise(img, 10)
    img.convert("RGB").save(PROMO / "github-hero.png", quality=95)


def draw_xhs_cover():
    img = Image.new("RGBA", (1080, 1440), (8, 10, 13, 255))
    d = ImageDraw.Draw(img)
    for j in range(90, 1440, 90):
        d.line((0, j, 1080, j), fill=(255, 255, 255, 5), width=1)
    d.rectangle((1000, 0, 1080, 1440), fill=(130, 247, 209, 255))
    text(d, (76, 78), "DESKTOP PRODUCTIVITY / 2026", 24, (130, 247, 209, 245), weight="mono")
    text(d, (76, 160), "这张便签\n可以缩进屏幕边缘", 86, (255, 255, 255, 246), weight="light", spacing=18)
    text(d, (78, 405), "不是新建一堆页面，而是一列真正独立的桌面便签窗口。", 32, (255, 255, 255, 186))
    draw_right_stack(d, 212, 540, 1.22)

    labels = [("01", "右侧自动吸附"), ("02", "窗口手动拉高"), ("03", "下面自动对齐"), ("04", "Todo 多行滚动")]
    rounded_rect(d, (58, 1108, 690, 1356), 10, (0, 0, 0, 116), outline=(255, 255, 255, 28))
    y = 1144
    for nb, label in labels:
        text(d, (78, y), nb, 26, (130, 247, 209, 245), weight="mono")
        text(d, (148, y - 4), label, 34, (255, 255, 255, 225), weight="bold")
        y += 58
    img = add_noise(img, 10)
    img.convert("RGB").save(PROMO / "xhs-cover.png", quality=95)


def draw_square():
    img = Image.new("RGBA", (1080, 1080), (8, 10, 13, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1080, 84), fill=(130, 247, 209, 255))
    text(d, (78, 138), "SIDE NOTES", 30, (130, 247, 209, 255), weight="mono")
    text(d, (78, 220), "桌面右侧\n便签列", 112, (255, 255, 255, 246), weight="light", spacing=20)
    text(d, (82, 528), "点一下展开\n再点一下缩回去", 46, (255, 255, 255, 194), spacing=12)
    draw_note_window(d, 580, 258, 360, 190, "工作", ["今天必须处理的三件事", "写完说明文档"], False)
    draw_note_window(d, 580, 468, 360, 160, "灵感", ["突然想到的功能点", "下次再做的小优化"], False)
    draw_note_window(d, 862, 654, 360, 112, "稍后", [], True)
    text(d, (78, 962), "Dockable notes for Windows desktop", 25, (255, 255, 255, 126), weight="mono")
    img = add_noise(img, 10)
    img.convert("RGB").save(PROMO / "square-cover.png", quality=95)


def draw_feature_card():
    img = Image.new("RGBA", (1080, 1440), (250, 250, 248, 255))
    d = ImageDraw.Draw(img)
    accent = (0, 47, 167, 255)
    text(d, (76, 80), "FEATURE MAP", 26, accent, weight="mono")
    text(d, (76, 152), "它解决的不是记录，\n是桌面上的位置。", 72, (10, 10, 10, 255), weight="light", spacing=14)

    rows = [
        ("01", "贴边", "自动吸附到屏幕右侧，不挡住主工作区。"),
        ("02", "缩进", "只露出标题标签，需要时点击拉出来。"),
        ("03", "分组", "多个独立便签窗口，自己决定分类。"),
        ("04", "滚动", "长 Todo 多行显示，窗口内部滚动。"),
        ("05", "对齐", "手动调整高度后，下面的便签自动下移。"),
    ]
    y = 480
    for nb, title, desc in rows:
        d.line((76, y - 24, 1004, y - 24), fill=(10, 10, 10, 55), width=2)
        text(d, (76, y), nb, 34, accent, weight="mono")
        text(d, (178, y - 6), title, 48, (10, 10, 10, 245), weight="bold")
        text(d, (372, y + 4), desc, 30, (10, 10, 10, 165))
        y += 156

    d.rectangle((76, 1268, 1004, 1274), fill=accent)
    text(d, (76, 1310), "Side Notes / notes kept at the edge of your desktop", 23, (10, 10, 10, 145), weight="mono")
    img.convert("RGB").save(PROMO / "feature-card.png", quality=95)


def draw_wechat_cover():
    img = Image.new("RGBA", (2100, 900), (8, 10, 13, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((1970, 0, 2100, 900), fill=(130, 247, 209, 255))
    text(d, (108, 86), "SIDE NOTES / DESKTOP TOOL", 26, (130, 247, 209, 255), weight="mono")
    text(d, (108, 186), "把便签贴在\n屏幕右侧", 100, (255, 255, 255, 246), weight="light", spacing=20)
    text(d, (112, 488), "一列独立窗口，自动吸附，点击缩进，只露出标题。", 42, (255, 255, 255, 188))
    for x, label in [(108, "多窗口"), (272, "贴边"), (398, "缩进"), (524, "本地保存")]:
        rounded_rect(d, (x, 660, x + 128, 714), 8, (255, 255, 255, 22), outline=(255, 255, 255, 50))
        text(d, (x + 22, 672), label, 26, (255, 255, 255, 220), weight="bold")
    draw_right_stack(d, 1246, 126, 1.05)
    img = add_noise(img, 10)
    img.convert("RGB").save(PROMO / "wechat-21x9-cover.png", quality=95)


def main():
    ASSETS.mkdir(exist_ok=True)
    PROMO.mkdir(exist_ok=True)
    draw_icon()
    draw_github_hero()
    draw_xhs_cover()
    draw_square()
    draw_feature_card()
    draw_wechat_cover()


if __name__ == "__main__":
    main()
