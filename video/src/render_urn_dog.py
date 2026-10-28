#!/usr/bin/env python3
"""Film o personalizacji urny dla psa (1920x1080, 30 kl./s, bez dźwięku, 15 s). Używa funkcji z render.py.
Użycie: python3 -I render_urn_dog.py WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
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
ASSETS = HERE / "assets_urn_dog"
FULL_CROP = (130, 280, 1870, 1790)  # the whole urn (photos are 2000x1999)
FRAG_CROP = (1020, 280, 1870, 1790)  # right part of the urn: plaque, name tag, edge of the paw
S = [0.0, 2.0, 5.8, 9.3, 12.9, 15.0]  # scene boundaries; each scene fades fully to white before the next


def ease(x):
    return R.ease(x)


def load(name):
    return Image.open(ASSETS / f"dog-{name}.jpg").convert("RGB")


def panel(name, height, crop):
    im = load(name).crop(crop)
    w = round(im.width * height / im.height)
    return im.resize((w, height), Image.LANCZOS).convert("RGBA")


def put(layer, img, cx, cy, alpha=1.0):
    if alpha <= 0.001:
        return
    im = img if alpha >= 0.999 else R.scale_alpha(img, alpha)
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.paste(im, (x, y))
    layer.alpha_composite(tmp)


def put_text(layer, text_layer, t, start, slide=True):
    a = ease((t - start) / FADE)
    if a <= 0.001:
        return
    lay = ImageChops.offset(text_layer, 0, round((1 - a) * 14)) if slide and a < 1 else text_layer
    layer.alpha_composite(R.scale_alpha(lay, a))


def zoom_crop(img, z, center, size):
    half = min(img.width, img.height) / 2 / z
    cx = min(max(center[0], half), img.width - half)
    cy = min(max(center[1], half), img.height - half)
    return img.resize((size, size), Image.LANCZOS, box=(cx - half, cy - half, cx + half, cy + half)).convert("RGBA")


# ------------------------------------------------------------------ scenes (t = seconds from the start of the scene)
T1 = R.text_block("PERSONALISATION", ["How to customize", "*your urn*"],
                  "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1100, title_size=104, centered=True)


def scene1(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, T1, t, 0.0)
    return layer


def _head():
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = R.ImageDraw.Draw(head)
    R.draw_runs(d, 150, 110, [("CHOOSE YOUR STYLE", R.opensans(26, 600))], R.GOLD, spacing=4)
    R.draw_runs(d, 150, 160, [("Your photo, ", R.playfair(76)), ("three ways", R.playfair(76, True))], R.DARK)
    d.rectangle([150, 270, 240, 272], fill=R.GOLD)
    d.text((150, 292), "Optional – a photo on the plaque is your choice", font=R.opensans(28, 400), fill=R.blend(R.DARK, 0.85))
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
CAP = {1: R.caption("Original photo", X1, 985), 2: R.caption("Colour, background removed", X2, 985),
       3: R.caption("Sketch style", X3, 985)}


def scene2(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put_text(layer, HEAD2, t, 0.0)
    a3 = ease((t - 1.7) / 0.8)  # fragment 3 slides out from under fragment 2 to the right
    put(layer, P[3], X2 + (X3 - X2) * a3, CY, 1.0 if t >= 1.7 else 0.0)
    a2 = ease((t - 1.0) / 0.8)  # fragment 2 slides out from under the whole urn 1
    put(layer, P[2], X2_START + (X2 - X2_START) * a2, CY, 1.0 if t >= 1.0 else 0.0)
    put(layer, P[1], X1, CY, ease((t - 0.2) / FADE))
    for i, ta in ((1, 0.5), (2, 1.8), (3, 2.5)):
        put_text(layer, CAP[i], t, ta)
    return layer


URN = load(3)
FRAME = 900
ZOOM_CENTER = {"tag": (1408, 1542), "paw": (737, 1144)}
ZOOM_TO = {"tag": 3.4, "paw": 2.3}
TX = {"tag": R.text_block("NAME AND DATES", ["Name and dates", "*of your beloved dog*"],
                          "Optional – added to the small plaque", 1090, H // 2),
      "paw": R.text_block("YOUR OWN WORDS", ["Your own quote,", "*if you wish*"],
                          "Add a short quote or message of your own", 1090, H // 2)}


def zoom_scene(which):
    def f(t):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        e = ease((t - 0.4) / 2.2)
        z = 1 + (ZOOM_TO[which] - 1) * e
        c = (1000 + (ZOOM_CENTER[which][0] - 1000) * e, 999.5 + (ZOOM_CENTER[which][1] - 999.5) * e)
        put(layer, zoom_crop(URN, z, c, FRAME), 540, H // 2, ease(t / FADE))
        put_text(layer, TX[which], t, 1.0)
        return layer
    return f


_lg, _lh = R.logo(380, W // 2, 0)
_et = R.end_texts(_lh + 50)
_boxes = [b for b in (_lg.getbbox(), _et.getbbox()) if b]
_dy = H // 2 - (min(b[1] for b in _boxes) + max(b[3] for b in _boxes)) // 2
LOGO, ETXT = ImageChops.offset(_lg, 0, _dy), ImageChops.offset(_et, 0, _dy)


def scene5(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(R.scale_alpha(LOGO, ease(t / FADE)))
    put_text(layer, ETXT, t, 0.7)
    return layer


SCENES = [scene1, scene2, zoom_scene("tag"), zoom_scene("paw"), scene5]


def frame(t):
    out = Image.new("RGBA", (W, H), R.WHITE + (255,))
    for i, fn in enumerate(SCENES):
        s, e = S[i], S[i + 1]
        if not (s <= t < e + 1e-9):
            continue
        tl = t - s
        a = 1.0
        if i < len(SCENES) - 1:
            a = 1 - ease((t - (e - FADE)) / FADE)  # fully white by the start of the next scene
        if a > 0.001:
            out.alpha_composite(R.scale_alpha(fn(tl), a))
    return out.convert("RGB")


def main():
    args = sys.argv[1:]
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
