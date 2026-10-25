#!/usr/bin/env python3
"""Render the Art-Dog ceramic plaque personalisation video (1920x1080, 30 fps, no audio).

Usage: python3 -I render.py OUTPUT.mp4 [--frames-dir DIR --at T [T ...]]
Everything the video shows lives in this file (texts, timing) and in assets/ and fonts/.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H, FPS, DURATION = 1920, 1080, 30, 15.0
GOLD = (0xD0, 0xA5, 0x49)
DARK = (0x58, 0x59, 0x5B)
WHITE = (255, 255, 255)
FADE = 0.45  # crossfade between scenes / panels, seconds

# ---------------------------------------------------------------- fonts
def playfair(size, italic=False):
    f = ImageFont.truetype(str(HERE / "fonts" / ("PlayfairDisplay-Italic.ttf" if italic else "PlayfairDisplay.ttf")), size)
    f.set_variation_by_axes([400])
    return f


def opensans(size, weight=400):
    f = ImageFont.truetype(str(HERE / "fonts" / "OpenSans.ttf"), size)
    f.set_variation_by_axes([weight, 100])  # axes: Weight, Width
    return f


# ---------------------------------------------------------------- text layers
def draw_runs(d, x, y, runs, fill, spacing=0):
    for t, f in runs:
        if spacing:
            for ch in t:
                d.text((x, y), ch, font=f, fill=fill)
                x += f.getlength(ch) + spacing
        else:
            d.text((x, y), t, font=f, fill=fill)
            x += f.getlength(t)
    return x


def wrap(text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def blend(c, a):
    return tuple(int(255 + (v - 255) * a) for v in c)


def text_block(label, title_lines, sub, x, cy, max_w=760, title_size=86, centered=False):
    """Label (gold caps), title (Georgia-style lines; *italic* runs), gold rule, subtitle.
    Returns RGBA layer the size of the frame, block vertically centred on cy."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lab_f, sub_f = opensans(26, 600), opensans(34, 400)
    tit_r, tit_i = playfair(title_size), playfair(title_size, True)
    line_h = int(title_size * 1.22)
    sub_lines = wrap(sub, sub_f, max_w)
    total = 26 + 30 + line_h * len(title_lines) + 34 + 3 + 34 + 46 * len(sub_lines)
    y = cy - total // 2

    def ox(width):
        return x - width // 2 if centered else x

    lw = sum(lab_f.getlength(c) + 4 for c in label)
    draw_runs(d, ox(lw), y, [(label, lab_f)], GOLD, spacing=4)
    y += 26 + 30
    for line in title_lines:
        runs, parts = [], line.split("*")
        for i, p in enumerate(parts):
            if p:
                runs.append((p, tit_i if i % 2 else tit_r))
        tw = sum(f.getlength(t) for t, f in runs)
        draw_runs(d, ox(int(tw)), y, runs, DARK)
        y += line_h
    y += 34
    rule_w = 90
    d.rectangle([ox(rule_w), y, ox(rule_w) + rule_w, y + 2], fill=GOLD)
    y += 3 + 34
    for sl in sub_lines:
        sw = sub_f.getlength(sl)
        d.text((ox(int(sw)), y), sl, font=sub_f, fill=blend(DARK, 0.85))
        y += 46
    return layer


def caption(text, cx, y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = opensans(30, 400)
    w = f.getlength(text)
    d.text((cx - w / 2, y), text, font=f, fill=blend(DARK, 0.9))
    return layer


# ---------------------------------------------------------------- image layers
CROP = (390, 195, 1610, 1810)  # the oval tile inside the 2000x2000 originals


def photo(name, height, cx, cy):
    im = Image.open(HERE / "assets" / f"{name}.jpg").convert("RGB").crop(CROP)
    w = round(im.width * height / im.height)
    im = im.resize((w, height), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(im, (cx - w // 2, cy - height // 2))
    return layer


def logo(width, cx, y):
    im = Image.open(HERE / "assets" / "logo.png").convert("RGBA")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(im, (cx - width // 2, y), im)
    return layer, h


def end_texts(y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = playfair(56, True)
    t = "In loving memory"
    d.text(((W - f.getlength(t)) / 2, y), t, font=f, fill=DARK)
    y += 100
    d.rectangle([W // 2 - 45, y, W // 2 + 45, y + 2], fill=GOLD)
    y += 30
    f2 = opensans(36, 400)
    t2 = "Handmade since 1993"
    d.text(((W - f2.getlength(t2)) / 2, y), t2, font=f2, fill=blend(DARK, 0.9))
    y += 70
    f3 = opensans(22, 600)
    t3 = "200 BREEDS  ·  ORIGINAL DESIGNS  ·  HANDMADE"
    w3 = sum(f3.getlength(c) + 4 for c in t3)
    draw_runs(d, (W - w3) / 2, y, [(t3, f3)], GOLD, spacing=4)
    return layer


# ---------------------------------------------------------------- timeline
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def fade(t, start, end=None, fade_in=FADE, fade_out=FADE):
    """Opacity of an element visible from `start` to `end` (None = stays)."""
    a = ease((t - start) / fade_in)
    if end is not None:
        a = min(a, 1 - ease((t - end) / fade_out))
    return a


def scale_alpha(layer, a):
    if a >= 0.999:
        return layer
    out = layer.copy()
    out.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    return out


def build():
    """Returns list of (layer, start, end, slide) where end None = until the end of its scene."""
    L = []
    S1, S2, S3, S4, S5 = 0.0, 2.5, 5.9, 9.5, 12.5

    # scene 1: intro
    L.append((text_block("PERSONALISATION", ["How to customize", "*your plaque*"],
                         "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1100,
                         title_size=104, centered=True), S1, S2 + FADE, True))

    # scene 2: A-D, same position, text on the right
    t2 = text_block("YOUR PHOTO", ["Any photo", "*you send us*"],
                    "Optional · attach it in the personalisation box", 1090, H // 2)
    L.append((t2, S2, S3 + FADE, True))
    step = (S3 - S2 - FADE) / 4
    for i, n in enumerate("ABCD"):
        start = S2 + i * step
        end = S2 + (i + 1) * step + (FADE if i < 3 else 0.0)
        L.append((photo(n, 880, 520, H // 2), start, end if i < 3 else S3 + FADE, False))

    # scenes 3 & 4: three panels
    def triple(label, title, caps, names, s, e):
        head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(head)
        lab_f = opensans(26, 600)
        draw_runs(d, 150, 110, [(label, lab_f)], GOLD, spacing=4)
        runs, parts = [], title.split("*")
        for i, p in enumerate(parts):
            if p:
                runs.append((p, playfair(76, True) if i % 2 else playfair(76)))
        draw_runs(d, 150, 160, runs, DARK)
        d.rectangle([150, 270, 240, 272], fill=GOLD)
        L.append((head, s, e, True))
        xs = [W // 2 - 640, W // 2, W // 2 + 640]
        for i, (n, c) in enumerate(zip(names, caps)):
            ps = s + 0.2 + i * 0.85
            L.append((photo(n, 640, xs[i], 625), ps, e, False))
            L.append((caption(c, xs[i], 968), ps, e, True))

    triple("CHOOSE YOUR STYLE", "Your photo, *three ways*",
           ["Original photo", "Colour, background removed", "Pencil sketch"],
           ["0", "0-color", "0-sketch"], S3, S4 + FADE)
    triple("ADD A DEDICATION", "Name and dates, *if you wish*",
           ["Portrait only", "With your pet's name", "With name and dates"],
           ["1", "1-name", "1-name-dates"], S4, S5 + FADE)

    # scene 5: end card
    lg, lh = logo(380, W // 2, 130)
    L.append((lg, S5 + 0.1, None, False))
    L.append((end_texts(130 + lh + 50), S5 + 0.8, None, True))
    return L


def compose(layers, t):
    frame = Image.new("RGBA", (W, H), WHITE + (255,))
    for layer, start, end, slide in layers:
        a = fade(t, start, end)
        if a <= 0.001:
            continue
        lay = layer
        if slide and a < 1:
            dy = round((1 - a) * 14)
            lay = ImageChops.offset(layer, 0, dy)
        frame = Image.alpha_composite(frame, scale_alpha(lay, a))
    return frame.convert("RGB")


def main():
    args = sys.argv[1:]
    out = args[0]
    layers = build()
    if "--at" in args:
        d = Path(args[args.index("--frames-dir") + 1])
        d.mkdir(parents=True, exist_ok=True)
        for t in [float(x) for x in args[args.index("--at") + 1:]]:
            compose(layers, t).save(d / f"t{t:05.2f}.png")
        return
    n = int(round(DURATION * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(compose(layers, i / FPS).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
