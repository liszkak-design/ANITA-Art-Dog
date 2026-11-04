#!/usr/bin/env python3
"""Film o personalizacji urny z popiersiem z brązu (wybór rasy, wybór koloru urny, imię, daty, cytat). 1920x1080, 30 kl./s, bez dźwięku, 15 s.
Zdjęcia: assets_urn_statue/<gatunek>/breed-1..5.jpg (rasy), colour-brown.jpg, colour-black.jpg.
Użycie: python3 -I render_urn_statue.py dog WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
FADE = R.FADE
SPECIES = "dog"
ASSETS = HERE / "assets_urn_statue" / SPECIES
S = [0.0, 1.9, 5.9, 8.4, 12.9, 15.0]
BREEDS = "100"
DESIGNS = "100+"
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


def load(name):
    return Image.open(ASSETS / f"{name}.jpg").convert("RGB")


# ---------------------------------------------------------------- scene 1
T1 = R.text_block("PERSONALISATION", ["How to customize the", "*engravings on your urn*"],
                  "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1300, title_size=96, centered=True)


def scene1(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, T1, t, 0.0)
    return layer


# ---------------------------------------------------------------- scene 2: the breeds cross-fade in one place (rounded white corners)
PW = 1000
RADIUS = 40
STATUE = {"dog": "BRONZE STATUE"}[SPECIES]


def rounded(im, r):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=r, fill=255)
    out = Image.new("RGB", im.size, (255, 255, 255))
    out.paste(im, mask=mask)
    return out


TILES = []
for n in range(1, 6):
    im = load(f"breed-{n}")
    im = im.resize((PW, round(im.height * PW / im.width)), Image.LANCZOS)
    TILES.append(rounded(im, RADIUS).convert("RGBA"))
PCX, PCY = 90 + PW // 2, 540
T2 = R.text_block(STATUE, ["Choose your", "*breed*"], f"{DESIGNS} breeds to choose from", 1160, H // 2, max_w=700, title_size=86)
STARTS2 = [0.2 + i * 0.55 for i in range(5)]


def scene2(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, tile in enumerate(TILES):
        put(layer, tile, PCX, PCY, ease((t - STARTS2[i]) / FADE))
    put_text(layer, T2, t, 0.2)
    return layer


# ---------------------------------------------------------------- scene 3: colour of the urn, black slides out from under brown
def urn_tile(name):
    im = load(name)
    a = np.asarray(im).astype(int)
    ys, xs = np.where((255 - a.min(axis=2)) > 40)
    im = im.crop((xs.min() - 14, ys.min() - 14, xs.max() + 15, ys.max() + 15))
    h = 640
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS).convert("RGBA")


BROWN, BLACK = urn_tile("colour-brown"), urn_tile("colour-black")
X_BROWN, X_BLACK = 330, 330 + BROWN.width + 90
X_START = X_BROWN + 40  # hidden behind the brown urn
CY3 = 520
T3 = R.text_block("THE URN", ["Choose your", "*colour*"], "Brown or black", 1160, H // 2, max_w=600, title_size=86)
CAPS3 = {0: R.caption("Brown", X_BROWN, 880), 1: R.caption("Black", X_BLACK, 880)}


def scene3(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, T3, t, 0.0)
    a = ease((t - 1.0) / 0.8)  # black slides out from under the brown one
    put(layer, BLACK, X_START + (X_BLACK - X_START) * a, CY3, 1.0 if t >= 1.0 else 0.0)
    put(layer, BROWN, X_BROWN, CY3, ease((t - 0.1) / FADE))
    put_text(layer, CAPS3[0], t, 0.5)
    put_text(layer, CAPS3[1], t, 1.7)
    return layer


# ---------------------------------------------------------------- scene 4: camera on the engraved plate: name and dates, then the quote
URN = load("breed-2")  # picked at random out of the five breed photos
FW, FH = 840, 560
FCX, FCY = 90 + FW // 2, H // 2
KEYS = [(0.0, 1000, 800, 2000), (0.9, 1000, 1250, 540), (2.2, 1000, 1250, 540), (3.1, 1000, 1340, 760), (4.5, 1000, 1340, 760)]


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


def tb(label, lines, sub):
    return R.text_block(label, lines, sub, 1010, H // 2, max_w=820, title_size=96)


TXB = {"nd": tb("NAME AND DATES", ["Your dog's", "*name and dates*"], "Engraved on the plate"),
       "quote": tb("YOUR OWN WORDS", ["Your own quote,", "*if you wish*"], "Add a short quote or message of your own")}


def scene4(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(layer, view(t), FCX, FCY, ease(t / FADE))
    put_text(layer, TXB["nd"], t, 0.9, 2.3)
    put_text(layer, TXB["quote"], t, 3.2)
    return layer


# ---------------------------------------------------------------- scene 5: end card
_lg, _lh = R.logo(380, W // 2, 0)
_et = R.end_texts(_lh + 50, BREEDS)
_boxes = [b for b in (_lg.getbbox(), _et.getbbox()) if b]
_dy = H // 2 - (min(b[1] for b in _boxes) + max(b[3] for b in _boxes)) // 2
LOGO, ETXT = ImageChops.offset(_lg, 0, _dy), ImageChops.offset(_et, 0, _dy)


def scene5(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(R.scale_alpha(LOGO, ease(t / FADE)))
    put_text(layer, ETXT, t, 0.7)
    return layer


SCENES = [scene1, scene2, scene3, scene4, scene5]


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
