#!/usr/bin/env python3
"""Film o personalizacji płytki ceramicznej z grafiką (portret rasy / własne zdjęcie / imię i daty). 1920x1080, 30 kl./s, bez dźwięku, 15 s.
Jak render.py (płytki ze szkicem), ale scena 3 bez szkicu: portret rasy, zdjęcie oryginalne, zdjęcie bez tła.
Zdjęcia: assets_plaque_graphics/ (A-D przykłady zdjęć klientów, 0 / 0-photo / 0-nobg, 1 / 1-name / 1-name-dates).
Użycie: python3 -I render_plaque_graphics.py WYJŚCIE.mp4 [--frames-dir KATALOG --at T [T ...]]
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
ASSETS = HERE / "assets_plaque_graphics"
BREEDS = "100"


def photo(name, height, cx, cy):
    im = Image.open(ASSETS / f"{name}.jpg").convert("RGB").crop(R.CROP)
    w = round(im.width * height / im.height)
    im = im.resize((w, height), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(im, (cx - w // 2, cy - height // 2))
    return layer


def build():
    L = []
    S1, S2, S3, S4, S5 = 0.0, 2.0, 5.3, 9.2, 12.9
    E1, E2, E3, E4 = S2 - FADE, S3 - FADE, S4 - FADE, S5 - FADE

    L.append((R.text_block("PERSONALISATION", ["How to customize", "*your plaque*"],
                           "Optional – order as shown, or make it your own", W // 2, H // 2, max_w=1100,
                           title_size=104, centered=True), S1, E1, True))

    t2 = R.text_block("YOUR PHOTO", ["Any photo", "*you send us*"],
                      "Optional · attach it in the personalisation box", 1090, H // 2)
    L.append((t2, S2, E2, True))
    step = (E2 - S2 - FADE) / 4
    for i, n in enumerate("ABCD"):
        start = S2 + i * step
        end = S2 + (i + 1) * step + FADE if i < 3 else E2
        L.append((photo(n, 880, 520, H // 2), start, end, False))

    def triple(label, title, caps, names, s, e):
        head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(head)
        R.draw_runs(d, 150, 110, [(label, R.opensans(26, 600))], R.GOLD, spacing=4)
        runs, parts = [], title.split("*")
        for i, p in enumerate(parts):
            if p:
                runs.append((p, R.playfair(76, True) if i % 2 else R.playfair(76)))
        R.draw_runs(d, 150, 160, runs, R.DARK)
        d.rectangle([150, 270, 240, 272], fill=R.GOLD)
        L.append((head, s, e, True))
        xs = [W // 2 - 640, W // 2, W // 2 + 640]
        for i, (n, c) in enumerate(zip(names, caps)):
            ps = s + 0.2 + i * 0.8
            L.append((photo(n, 640, xs[i], 625), ps, e, False))
            L.append((R.caption(c, xs[i], 968), ps, e, True))

    triple("CHOOSE YOUR PORTRAIT", "Breed portrait, *or your own photo*",
           ["Breed portrait", "Your original photo", "Background removed"],
           ["0", "0-photo", "0-nobg"], S3, E3)
    triple("ADD A DEDICATION", "Name and dates, *if you wish*",
           ["Portrait only", "With your pet's name", "With name and dates"],
           ["1", "1-name", "1-name-dates"], S4, E4)

    lg, lh = R.logo(380, W // 2, 0)
    et = R.end_texts(lh + 50, BREEDS)
    boxes = [b for b in (lg.getbbox(), et.getbbox()) if b]
    top, bottom = min(b[1] for b in boxes), max(b[3] for b in boxes)
    dy = H // 2 - (top + bottom) // 2
    L.append((ImageChops.offset(lg, 0, dy), S5, None, False))
    L.append((ImageChops.offset(et, 0, dy), S5 + 0.7, None, True))
    return L


def main():
    args = sys.argv[1:]
    layers = build()
    if "--at" in args:
        d = Path(args[args.index("--frames-dir") + 1])
        d.mkdir(parents=True, exist_ok=True)
        for t in [float(x) for x in args[args.index("--at") + 1:]]:
            R.compose(layers, t).save(d / f"t{t:05.2f}.png")
        return
    n = int(round(R.DURATION * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", args[0]]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(R.compose(layers, i / FPS).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
