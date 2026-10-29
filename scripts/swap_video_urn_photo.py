#!/usr/bin/env python3
"""Replace the product photo of the urn in the first scene of an existing urn video with another photo of the same urn
(same studio framing), keeping the slow zoom and the fades of the original.

The old urn is not available as a file, so its on-screen transform is measured from the video: bounding box of the
old urn on frames where it is fully visible -> scale (linear in time) and position (linear in scale). For every frame
of the scene the new photo is drawn with that transform and with the opacity fitted to the frame; everything outside
the urn silhouette (texts, the next scene fading in on the right) is left untouched.

Usage:
  python3 -I scripts/swap_video_urn_photo.py IN.mp4 OUT.mp4 NEW.jpg [--seconds 3.0] [--limit-x 965] [--diag]
"""
import argparse
import subprocess

import numpy as np
from PIL import Image, ImageFilter

W, H, FPS = 1920, 1080, 30
PAD = 900
FIT_FRAMES = range(15, 61, 3)  # old urn fully visible, before the cross-fade into the next scene


def read_frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3).copy()
    p.wait()


def bbox(a, thr=40):
    m = (255 - a.min(axis=2)) > thr
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("new")
    ap.add_argument("--seconds", type=float, default=3.0, help="patch only the first N seconds (scene 1)")
    ap.add_argument("--limit-x", type=int, default=965, help="the urn lives left of this x; the next scene starts right of it")
    ap.add_argument("--diag", action="store_true", help="print fitted transform and per-frame opacity, write nothing")
    a = ap.parse_args()
    lx = a.limit_x

    new = Image.open(a.new).convert("RGB")
    nw, nh = new.size
    narr = np.asarray(new).astype(int)
    nb = bbox(narr)
    padded = Image.new("RGB", (nw + 2 * PAD, nh + 2 * PAD), (255, 255, 255))
    padded.paste(new, (PAD, PAD))

    # ---- measure the old urn on frames where it is fully visible
    meas = {}
    for i, fr in enumerate(read_frames(a.inp)):
        if i in FIT_FRAMES:
            meas[i] = bbox(fr[:, :lx].astype(int))
        if i > max(FIT_FRAMES):
            break
    ts = np.array([i / FPS for i in meas])
    sx = np.array([(b[2] - b[0]) / (nb[2] - nb[0]) for b in meas.values()])
    sy = np.array([(b[3] - b[1]) / (nb[3] - nb[1]) for b in meas.values()])
    s = (sx + sy) / 2
    oxs = np.array([((b[0] - s_ * nb[0]) + (b[2] - s_ * nb[2])) / 2 for b, s_ in zip(meas.values(), s)])
    oys = np.array([((b[1] - s_ * nb[1]) + (b[3] - s_ * nb[3])) / 2 for b, s_ in zip(meas.values(), s)])
    s1, s0 = np.polyfit(ts, s, 1)
    bx, ax_ = np.polyfit(s, oxs, 1)
    by, ay_ = np.polyfit(s, oys, 1)
    print(f"skala(t) = {s0:.4f} + {s1:.4f} t | x = {ax_:.1f} + {bx:.1f} s | y = {ay_:.1f} + {by:.1f} s")

    def render(t):
        sc = s0 + s1 * t
        ox, oy = ax_ + bx * sc, ay_ + by * sc
        # frame pixel (x, y) <- source pixel ((x - ox) / sc, (y - oy) / sc); canvas = frame columns [0, lx)
        box = ((0 - ox) / sc + PAD, (0 - oy) / sc + PAD, (lx - ox) / sc + PAD, (H - oy) / sc + PAD)
        return np.asarray(padded.resize((lx, H), Image.LANCZOS, box=box)).astype(float)

    # plaque of the new photo (not on the old one) is excluded from the opacity fit
    plaque = np.zeros((nh, nw), bool)
    plaque[470:960, 1020:1540] = True

    enc = None
    if not a.diag:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                "-i", "-", "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "15",
                                "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    nmax = int(a.seconds * FPS)
    for i, fr in enumerate(read_frames(a.inp)):
        if i < nmax:
            t = i / FPS
            n = render(t)
            reg = fr[:, :lx].astype(float)
            dn = 255 - n.min(axis=2)
            sil = dn > 40
            # opacity of the old urn: least squares on the urn silhouette, plaque area excluded
            sc = s0 + s1 * t
            ox, oy = ax_ + bx * sc, ay_ + by * sc
            pm = np.asarray(Image.fromarray(plaque.astype(np.uint8) * 255).resize((int(nw * sc), int(nh * sc)))) > 127
            pmask = np.zeros((H, lx), bool)
            x0, y0 = int(round(ox)), int(round(oy))
            sub = pm[:max(0, min(pm.shape[0], H - y0)), :max(0, min(pm.shape[1], lx - x0))]
            if sub.size and x0 >= 0 and y0 >= 0:
                pmask[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = sub
            use = sil & ~pmask
            u = 255 - reg.mean(axis=2)
            v = 255 - n.mean(axis=2)
            alpha = float(np.clip((u[use] * v[use]).sum() / max((v[use] ** 2).sum(), 1e-6), 0, 1)) if use.sum() > 100 else 0.0
            if a.diag:
                print(i, round(t, 2), "alpha", round(alpha, 3))
            elif alpha > 0.02:
                old = (255 - reg.mean(axis=2)) > 3  # everything the old urn painted
                mask = old | sil
                mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 127
                soft = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
                blend = 255 - alpha * (255 - n)
                out = reg * (1 - soft[..., None]) + blend * soft[..., None]
                fr[:, :lx] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        if enc:
            enc.stdin.write(fr.tobytes())
        elif i >= nmax:
            break
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    main()
