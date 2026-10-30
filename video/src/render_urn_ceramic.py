#!/usr/bin/env python3
"""Film o personalizacji urny z płytką ceramiczną (portret rasy / własne zdjęcie, tabliczka imienna, cytat). 1920x1080, 30 kl./s, bez dźwięku, 15 s.
Zdjęcia: assets_urn_ceramic/<gatunek>/<gatunek>-1.jpg (portret rasy), -2 (zdjęcie oryginalne), -3 (bez tła).
Użycie: python3 -I render_urn_ceramic.py dog WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
FADE = R.FADE
SPECIES = "dog"
ASSETS = HERE / "assets_urn_ceramic" / SPECIES
S = [0.0, 2.0, 5.8, 12.9, 15.0]
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


# ---------------------------------------------------------------- scene 2: breed portrait, then the photo options slide out from under it
FULL_CROP = (130, 300, 1890, 1840)  # the whole urn (photos are 2000x2000)
FRAG_CROP = (1020, 300, 1890, 1840)  # right part of the urn: oval portrait and name plate


def panel(n, height, crop):
    im = load(n).crop(crop)
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS).convert("RGBA")


def _head():
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(head)
    R.draw_runs(d, 150, 110, [("CHOOSE YOUR PORTRAIT", R.opensans(26, 600))], R.GOLD, spacing=4)
    R.draw_runs(d, 150, 160, [("Breed portrait, ", R.playfair(76)), ("or your own photo", R.playfair(76, True))], R.DARK)
    d.rectangle([150, 270, 240, 272], fill=R.GOLD)
    d.text((150, 292), "Standard: 1 of 100 breed portraits · your photo is optional", font=R.opensans(28, 400), fill=R.blend(R.DARK, 0.85))
    return head


HEAD2 = _head()
PH = 620
P = {1: panel(1, PH, FULL_CROP), 2: panel(2, PH, FRAG_CROP), 3: panel(3, PH, FRAG_CROP)}
GAP = 70
X0 = (W - (P[1].width + P[2].width + P[3].width + 2 * GAP)) // 2
X1 = X0 + P[1].width // 2
X2 = X0 + P[1].width + GAP + P[2].width // 2
X3 = X0 + P[1].width + GAP + P[2].width + GAP + P[3].width // 2
X2_START = X1 + 200  # fully hidden behind the whole urn
CY = 655
CAP = {1: R.caption("Breed portrait", X1, 985), 2: R.caption("Your original photo", X2, 985),
       3: R.caption("Background removed", X3, 985)}


def scene2(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, HEAD2, t, 0.0)
    a3 = ease((t - 1.7) / 0.8)  # panel 3 slides out from under panel 2 to the right
    put(layer, P[3], X2 + (X3 - X2) * a3, CY, 1.0 if t >= 1.7 else 0.0)
    a2 = ease((t - 1.0) / 0.8)  # panel 2 slides out from under the whole urn
    put(layer, P[2], X2_START + (X2 - X2_START) * a2, CY, 1.0 if t >= 1.0 else 0.0)
    put(layer, P[1], X1, CY, ease((t - 0.2) / FADE))
    for i, ta in ((1, 0.5), (2, 1.8), (3, 2.5)):
        put_text(layer, CAP[i], t, ta)
    return layer


# ---------------------------------------------------------------- scene 3: camera over the urn (name plate, then the quote plaque)
URN = load(3)
FW, FH = 840, 560
FCX, FCY = 90 + FW // 2, H // 2
KEYS = [(0.0, 1000, 1000, 2000), (0.9, 1411, 1521, 760), (3.2, 1411, 1521, 760), (4.2, 665, 1200, 1120), (7.0, 665, 1200, 1120)]


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
    put_text(layer, TXB["nd"], t, 1.0, 3.3)
    put_text(layer, TXB["quote"], t, 4.3)
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
