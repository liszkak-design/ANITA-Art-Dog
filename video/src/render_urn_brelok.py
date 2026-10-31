#!/usr/bin/env python3
"""Film o personalizacji urny z małą posrebrzaną płaskorzeźbą (wybór wizerunku, imię, daty, cytat). 1920x1080, 30 kl./s, bez dźwięku, 15 s.
Zdjęcia: assets_urn_brelok/<gatunek>/<gatunek>-1..5.jpg (przykładowe urny), -6.jpg (główna).
Użycie: python3 -I render_urn_brelok.py dog WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
FADE = R.FADE
SPECIES = "dog"
ASSETS = HERE / "assets_urn_brelok" / SPECIES
S = [0.0, 2.0, 6.4, 12.9, 15.0]
BREEDS = "200"
DESIGNS = "150+"
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
T1 = R.text_block("PERSONALISATION", ["How to customize the", "*engravings on your urn*"],
                  "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1300, title_size=96, centered=True)


def scene1(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, T1, t, 0.0)
    return layer


# ---------------------------------------------------------------- scene 2: the reliefs cross-fade on the same urn
CROP = (130, 270, 1900, 1830)  # the whole urn (photos are 2000x2000, identical framing)
PW = 1000
TILES = []
for n in range(1, 7):
    im = load(n).crop(CROP)
    TILES.append(im.resize((PW, round(im.height * PW / im.width)), Image.LANCZOS).convert("RGBA"))
PCX, PCY = 90 + PW // 2, 520
T2 = R.text_block("SILVER-PLATED RELIEF", ["Choose your", "*breed*"], f"{DESIGNS} designs to choose from", 1160, H // 2, max_w=700, title_size=86)
STARTS2 = [0.2 + i * 0.6 for i in range(6)]


def scene2(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, tile in enumerate(TILES):
        put(layer, tile, PCX, PCY, ease((t - STARTS2[i]) / FADE))
    put_text(layer, T2, t, 0.2)
    return layer


# ---------------------------------------------------------------- scene 3: camera over the urn: name, dates, quote
URN = load(6)
FW, FH = 840, 560
FCX, FCY = 90 + FW // 2, H // 2
KEYS = [(0.0, 1000, 1000, 2000), (0.9, 580, 906, 700), (2.1, 580, 906, 700), (3.0, 1467, 905, 700), (4.0, 1467, 905, 700),
        (5.0, 1020, 1144, 1400), (6.5, 1020, 1144, 1400)]


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


TXB = {"name": tb("NAME", ["Your dog's", "*name*"], "Engraved on the small plaque"),
       "dates": tb("DATES", ["Dates of", "*life*"], "Engraved on the small plaque"),
       "quote": tb("YOUR OWN WORDS", ["Your own quote,", "*if you wish*"], "Add a short quote or message of your own")}


def scene3(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(layer, view(t), FCX, FCY, ease(t / FADE))
    put_text(layer, TXB["name"], t, 1.0, 2.2)
    put_text(layer, TXB["dates"], t, 3.1, 4.1)
    put_text(layer, TXB["quote"], t, 5.1)
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
