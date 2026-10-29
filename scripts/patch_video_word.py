#!/usr/bin/env python3
"""Replace one word of on-screen text in an existing video (e.g. a wrong breed name) without access to its source.

The old word is measured on a clean reference frame (exact glyph coverage and colour), its visibility is estimated on
every frame (fades, translucent transitions), the old glyphs are painted out from the surrounding background and the
new word is drawn with the same position, colour and visibility. Everything else in the video stays untouched.

Usage:
  python3 -I scripts/patch_video_word.py IN.mp4 OUT.mp4 --old Saluki --new Sloughi --ref-frame 46 \
      --region 1130 365 1440 470 --font-size 79 --font FONT.ttf [--diag] [--seconds 5]
"""
import argparse
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    w, h, fr = out.strip(",").split(",")[:3]
    n, d = fr.split("/")
    return int(w), int(h), float(n) / float(d)


def read_frames(path, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 3).copy()
    p.wait()


def dilate(mask, k):
    im = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(k))
    return np.asarray(im) > 127


def vshift(a, dy):
    out = np.zeros_like(a)
    if dy >= 0:
        out[dy:] = a[:a.shape[0] - dy]
    else:
        out[:dy] = a[-dy:]
    return out


def blur_fill(px, keep, radius=9):
    """Normalized convolution: fill the pixels where keep is False from the pixels where it is True."""
    k = np.exp(-0.5 * (np.arange(-3 * radius, 3 * radius + 1) / radius) ** 2)
    k /= k.sum()

    def conv(a):
        a = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 0, a)
        return np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, a)

    wgt = keep.astype(float)
    out = np.empty_like(px, dtype=float)
    den = conv(wgt) + 1e-6
    for c in range(3):
        out[..., c] = conv(px[..., c] * wgt) / den
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--ref-frame", type=int, required=True, help="0-based frame where the old word is fully visible on white")
    ap.add_argument("--region", type=int, nargs=4, required=True, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--font", required=True)
    ap.add_argument("--font-size", type=int, required=True)
    ap.add_argument("--origin", type=int, nargs=2, default=None, help="where to draw the new word inside the region (x y); default = fitted")
    ap.add_argument("--max-dy", type=int, default=30, help="largest vertical slide of the text during fade-in (px)")
    ap.add_argument("--seconds", type=float, default=6.0, help="patch only the first N seconds")
    ap.add_argument("--diag", action="store_true", help="print the visibility of the old word per frame and exit")
    a = ap.parse_args()

    w, h, fps = probe(a.inp)
    x0, y0, x1, y1 = a.region
    nmax = int(a.seconds * fps)

    # ---- reference: exact coverage of the old word
    ref = None
    for i, fr in enumerate(read_frames(a.inp, w, h)):
        if i == a.ref_frame:
            ref = fr
            break
    reg = ref[y0:y1, x0:x1].astype(float)
    g = reg.mean(axis=2)
    dark = g < np.percentile(g, 1.5)
    color = reg[dark].mean(axis=0)
    gc = color.mean()
    cov = np.clip((255 - g) / (255 - gc), 0, 1)
    cov[cov < 0.04] = 0
    glyph = cov > 0.9
    near = dilate(cov > 0.02, 15)
    ring = ~near
    print("kolor tekstu RGB:", color.round(0), "| piksele glifów:", int(glyph.sum()), file=sys.stderr)

    # ---- new word: fit font origin on the old word so that the baseline and left edge coincide
    font = ImageFont.truetype(a.font, a.font_size)
    try:
        font.set_variation_by_axes([400])
    except Exception:
        pass

    def draw(word, ox, oy):
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).text((ox, oy), word, font=font, fill=255)
        return np.asarray(m).astype(float) / 255

    if a.origin:
        ox, oy = a.origin
    else:
        best = None
        for oy_ in range(-10, 60):
            for ox_ in range(0, 80):
                c = draw(a.old, ox_, oy_)
                s = (c * cov).sum() / np.sqrt((c ** 2).sum() * (cov ** 2).sum() + 1e-9)
                if best is None or s > best[0]:
                    best = (s, ox_, oy_)
        print("dopasowanie czcionki do starego słowa (korelacja, x, y):", best, file=sys.stderr)
        ox, oy = best[1], best[2]
    new_cov = draw(a.new, ox, oy)

    enc = None
    if not a.diag:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
                                "-i", "-", "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "15", "-colorspace", "bt470bg", "-color_range", "tv",
                                "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for i, fr in enumerate(read_frames(a.inp, w, h)):
        if i < nmax:
            reg = fr[y0:y1, x0:x1].astype(float)
            gg = reg.mean(axis=2)
            best = None
            for dy in range(0, a.max_dy + 1):  # text slides up while it fades in: find the vertical offset of this frame
                cs = vshift(cov, dy)
                gl, rg = cs > 0.9, ~dilate(cs > 0.02, 15)
                contrast = gg[rg].mean() - gg[gl].mean()
                if best is None or contrast > best[0]:
                    best = (contrast, dy)
            dy = best[1]
            cs = vshift(cov, dy)
            glyph_s, ring_s = cs > 0.9, ~dilate(cs > 0.02, 15)
            bgm = gg[ring_s].mean()
            alpha = float(np.clip((bgm - gg[glyph_s].mean()) / max(bgm - gc, 1e-6), 0, 1))
            if a.diag:
                print(i, round(i / fps, 2), "alpha", round(alpha, 2), "dy", dy, "tło", round(bgm))
            elif alpha > 0.03:
                old_mask = dilate(cs * alpha > 0.03, 5)
                if bgm > 250:  # flat white background: nothing to estimate
                    fill = np.full_like(reg, 255.0)
                else:
                    fill = blur_fill(reg, ~dilate(cs * alpha > 0.02, 11))
                soft = np.asarray(Image.fromarray((old_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
                base = reg * (1 - soft[..., None]) + fill * soft[..., None]
                nc = vshift(new_cov, dy)
                out = base * (1 - alpha * nc[..., None]) + color * alpha * nc[..., None]
                fr[y0:y1, x0:x1] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        if enc:
            enc.stdin.write(fr.tobytes())
        elif i >= nmax:
            break
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    main()
