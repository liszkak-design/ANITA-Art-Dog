#!/usr/bin/env python3
"""Film o personalizacji urny z płytką ceramiczną (portret rasy / własne zdjęcie, tabliczka imienna, cytat). 1920x1080, 30 kl./s, bez dźwięku, 15 s.
Zdjęcia: assets_urn_ceramic/<gatunek>/<gatunek>-1.jpg (portret rasy), -2 (zdjęcie oryginalne), -3 (bez tła).
Użycie: python3 -I render_urn_ceramic.py dog WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
FADE = R.FADE
SPECIES = "dog"
ASSETS = HERE / "assets_urn_ceramic" / SPECIES
S = [0.0, 2.0, 7.0, 12.9, 15.0]
BREEDS = "100"
ease = R.ease


def put(layer, img, cx, cy, alpha=1.0):
    if alpha <= 0.001:
        return
    im = img if alpha >= 0.999 else R.scale_alpha(img, alpha)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.paste(im, (round(cx - im.width / 2), round(cy - im.height / 2)))
    layer.alpha_composite(tmp)


def put_text(layer, tl, t, start, end=None, slide=True):
    a = ease((t - start) / FADE)
    if end is not None:
        a = min(a, 1 - ease((t - end) / FADE))
    if a <= 0.001:
        return
    lay = ImageChops.offset(tl, 0, round((1 - a) * 14)) if slide and a < 1 else tl
    layer.alpha_composite(R.scale_alpha(lay, a))


def load(n):
    return Image.open(ASSETS / f"{SPECIES}-{n}.jpg").convert("RGB")


# ---------------------------------------------------------------- scene 1
T1 = R.text_block("PERSONALISATION", ["How to customize", "*your urn*"],
                  "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1100, title_size=104, centered=True)


def scene1(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, T1, t, 0.0)
    return layer


# ---------------------------------------------------------------- scene 2: breed portrait -> your photo -> background removed
CROP = (130, 300, 1890, 1840)  # the whole urn (photos are 2000x2000)
PW = 1000
IMGS = []
for n in (1, 2, 3):
    im = load(n).crop(CROP)
    IMGS.append(im.resize((PW, round(im.height * PW / im.width)), Image.LANCZOS).convert("RGBA"))
PCX, PCY = 90 + PW // 2, 520
TX2 = 1160
CAPS = ["Standard: 1 of 100 portraits", "Optional: your original photo", "Optional: background removed"]
_blocks = [R.text_block("CHOOSE YOUR PORTRAIT", ["Breed portrait,", "*or your own photo*"], c, TX2, H // 2, max_w=700, title_size=76) for c in CAPS]
_static = R.text_block("CHOOSE YOUR PORTRAIT", ["Breed portrait,", "*or your own photo*"], " ", TX2, H // 2, max_w=700, title_size=76)
SUB_BAND = (0, 650, W, 780)
SUBL = []
for b in _blocks:
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.paste(b.crop(SUB_BAND), (SUB_BAND[0], SUB_BAND[1]))
    SUBL.append(lay)


def scene2(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(layer, IMGS[0], PCX, PCY, ease((t - 0.2) / FADE))
    put(layer, IMGS[1], PCX, PCY, ease((t - 1.4) / 0.6))
    put(layer, IMGS[2], PCX, PCY, ease((t - 2.9) / 0.6))
    put_text(layer, _static, t, 0.2)
    for i, (a0, a1) in enumerate(((0.3, 1.5), (1.4, 3.0), (2.9, None))):
        put_text(layer, SUBL[i], t, a0, a1, slide=False)
    return layer


# ---------------------------------------------------------------- scene 3: camera over the urn (name plate, then the quote plaque)
URN = load(3)
FW, FH = 840, 560
FCX, FCY = 90 + FW // 2, H // 2
KEYS = [(0.0, 1000, 1000, 2000), (0.9, 1411, 1521, 760), (2.9, 1411, 1521, 760), (3.9, 735, 1150, 900), (5.9, 735, 1150, 900)]


def cam(t):
    for (t0, x0, y0, w0), (t1, x1, y1, w1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            e = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, w0 + (w1 - w0) * e
    return KEYS[-1][1:]


def view(t):
    cx, cy, w = cam(t)
    w = min(w, URN.width, URN.height * FW / FH)
    h = w * FH / FW
    cx = min(max(cx, w / 2), URN.width - w / 2)
    cy = min(max(cy, h / 2), URN.height - h / 2)
    return URN.resize((FW, FH), Image.LANCZOS, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)).convert("RGBA")


TXB = {"nd": R.text_block("NAME AND DATES", ["Your dog's", "*name and dates*"], "Engraved on the nameplate", 1010, H // 2, max_w=820, title_size=96),
       "quote": R.text_block("YOUR OWN WORDS", ["Your own quote,", "*if you wish*"], "Changed on request", 1010, H // 2, max_w=820, title_size=96)}


def scene3(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(layer, view(t), FCX, FCY, ease(t / FADE))
    put_text(layer, TXB["nd"], t, 1.0, 3.0)
    put_text(layer, TXB["quote"], t, 4.0)
    return layer


# ---------------------------------------------------------------- scene 4: end card
_lg, _lh = R.logo(380, W // 2, 0)
_et = R.end_texts(_lh + 50, BREEDS)
_boxes = [b for b in (_lg.getbbox(), _et.getbbox()) if b]
_dy = H // 2 - (min(b[1] for b in _boxes) + max(b[3] for b in _boxes)) // 2
LOGO, ETXT = ImageChops.offset(_lg, 0, _dy), ImageChops.offset(_et, 0, _dy)


def scene4(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(R.scale_alpha(LOGO, ease(t / FADE)))
    put_text(layer, ETXT, t, 0.7)
    return layer


SCENES = [scene1, scene2, scene3, scene4]


def frame(t):
    out = Image.new("RGBA", (W, H), R.WHITE + (255,))
    for i, fn in enumerate(SCENES):
        s, e = S[i], S[i + 1]
        if not (s <= t < e + 1e-9):
            continue
        a = 1.0
        if i < len(SCENES) - 1:
            a = 1 - ease((t - (e - FADE)) / FADE)
        if a > 0.001:
            out.alpha_composite(R.scale_alpha(fn(t - s), a))
    return out.convert("RGB")


def main():
    args = sys.argv[2:]
    if "--at" in args:
        d = Path(args[args.index("--frames-dir") + 1])
        d.mkdir(parents=True, exist_ok=True)
        for t in [float(x) for x in args[args.index("--at") + 1:]]:
            frame(t).save(d / f"t{t:05.2f}.png")
        return
    n = int(round(R.DURATION * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", args[0]]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
