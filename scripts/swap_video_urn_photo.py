#!/usr/bin/env python3
"""Replace the product photo of the urn in an existing urn video (scenes where the urn photo is shown full size,
e.g. the first and the last scene) with another photo of the same urn (same studio framing). The slow zoom and
the fades of the original are kept.

The old urn is not available as a file, so its on-screen transform is measured from the video, per scene: bounding box
of the old urn on frames where it is fully visible -> scale (linear in time) and position (linear in scale).
For every frame of a scene the new photo is drawn with that transform and with the opacity fitted to the frame.
  mask mode  : the urn silhouette is replaced (texts and the neighbouring scene outside the silhouette stay untouched).
  delta mode : used while the urn fades in over another scene (its photo and text overlap the urn):
               out = frame + alpha * (new - old), where `old` is the old urn taken from a clean reference frame.

Usage:
  python3 -I scripts/swap_video_urn_photo.py IN.mp4 OUT.mp4 NEW.jpg [--diag]
Scenes are defined in SCENES below (seconds, pixels; measured on the 15 s Art-Dog urn films, 1920x1080, 30 fps).
"""
import argparse
import subprocess

import numpy as np
from PIL import Image, ImageFilter

W, H, FPS = 1920, 1080, 30
PAD = 900
SCENES = [
    # x0, x1: columns the urn lives in; t0, t1: frames patched; fit: clean frames used to measure the transform;
    # delta_until: use delta mode before this time; ref: clean frame of the old urn; excl: boxes ignored when fitting opacity
    dict(name="scena 1", x0=0, x1=965, t0=0.0, t1=3.0, fit=range(15, 61, 3), delta_until=0.0, ref=None, excl=[]),
    dict(name="scena ostatnia", x0=960, x1=1920, t0=10.2, t1=13.0, fit=range(339, 376, 3), delta_until=11.4, ref=363,
         excl=[(0, 1100, 0, H), (1100, 1920, 360, 640)]),
]


def read_frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3).copy()
    p.wait()


def bbox(a, x0, x1, thr=40):
    m = (255 - a[:, x0:x1].min(axis=2)) > thr
    ys, xs = np.where(m)
    return xs.min() + x0, ys.min(), xs.max() + x0, ys.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("new")
    ap.add_argument("--diag", action="store_true", help="print fitted transforms and per-frame opacity, write nothing")
    a = ap.parse_args()

    new = Image.open(a.new).convert("RGB")
    nw, nh = new.size
    nb = bbox(np.asarray(new).astype(int), 0, nw)
    padded = Image.new("RGB", (nw + 2 * PAD, nh + 2 * PAD), (255, 255, 255))
    padded.paste(new, (PAD, PAD))
    plaque_arr = np.zeros((nh, nw), np.uint8)
    plaque_arr[470:960, 1020:1540] = 255  # plaque of the new photo (not on the old one): excluded from the opacity fit
    plaque = Image.fromarray(plaque_arr)

    # ---- pass 1: measure the old urn and grab reference frames
    need = {i for sc in SCENES for i in sc["fit"]} | {sc["ref"] for sc in SCENES if sc["ref"]}
    last = max(need)
    meas, refs = {}, {}
    for i, fr in enumerate(read_frames(a.inp)):
        if i in need:
            for k, sc in enumerate(SCENES):
                if i in sc["fit"]:
                    meas[(k, i)] = bbox(fr.astype(int), sc["x0"], sc["x1"])
                if i == sc["ref"]:
                    refs[k] = fr
        if i >= last:
            break

    fits = []
    for k, sc in enumerate(SCENES):
        items = [(i, b) for (kk, i), b in meas.items() if kk == k]
        ts = np.array([i / FPS for i, _ in items])
        s = np.array([((b[2] - b[0]) / (nb[2] - nb[0]) + (b[3] - b[1]) / (nb[3] - nb[1])) / 2 for _, b in items])
        oxs = np.array([((b[0] - s_ * nb[0]) + (b[2] - s_ * nb[2])) / 2 for (_, b), s_ in zip(items, s)])
        oys = np.array([((b[1] - s_ * nb[1]) + (b[3] - s_ * nb[3])) / 2 for (_, b), s_ in zip(items, s)])
        s1, s0 = np.polyfit(ts, s, 1)
        bx, ax_ = np.polyfit(s, oxs, 1)
        by, ay_ = np.polyfit(s, oys, 1)
        print(f"{sc['name']}: skala(t) = {s0:.4f} + {s1:.4f} t | x = {ax_:.1f} + {bx:.1f} s | y = {ay_:.1f} + {by:.1f} s")
        fits.append((s0, s1, ax_, bx, ay_, by))

    def tf(k, t):
        s0, s1, ax_, bx, ay_, by = fits[k]
        sc = s0 + s1 * t
        return sc, ax_ + bx * sc, ay_ + by * sc

    def render_new(k, t):
        """New photo in frame coordinates (full frame, float RGB)."""
        sc, ox, oy = tf(k, t)
        x0, x1 = SCENES[k]["x0"], SCENES[k]["x1"]
        box = ((x0 - ox) / sc + PAD, (0 - oy) / sc + PAD, (x1 - ox) / sc + PAD, (H - oy) / sc + PAD)
        out = np.full((H, W, 3), 255.0)
        out[:, x0:x1] = np.asarray(padded.resize((x1 - x0, H), Image.LANCZOS, box=box)).astype(float)
        return out

    def resample(img, k, t_from, t_to):
        """Move an image of the urn drawn at time t_from to the scale/position of time t_to."""
        sf, oxf, oyf = tf(k, t_from)
        st, oxt, oyt = tf(k, t_to)
        r = st / sf
        data = (1 / r, 0, oxf - oxt / r, 0, 1 / r, oyf - oyt / r)
        return np.asarray(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).transform((W, H), Image.AFFINE, data, Image.BICUBIC,
                                                                                            fillcolor=(255, 255, 255))).astype(float)

    ref_old, ref_new = {}, {}
    for k, sc in enumerate(SCENES):
        if sc["ref"]:
            ref_old[k] = refs[k].astype(float)
            ref_new[k] = render_new(k, sc["ref"] / FPS)

    def plaque_mask(k, t):
        sc, ox, oy = tf(k, t)
        pm = np.asarray(plaque.resize((int(nw * sc), int(nh * sc)))) > 127
        out = np.zeros((H, W), bool)
        x0, y0 = int(round(ox)), int(round(oy))
        sub = pm[:max(0, min(pm.shape[0], H - y0)), :max(0, min(pm.shape[1], W - x0))]
        if sub.size and x0 >= 0 and y0 >= 0:
            out[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = sub
        return out

    enc = None
    if not a.diag:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                "-i", "-", "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "15", "-colorspace", "bt470bg", "-color_range", "tv",
                                "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for i, fr in enumerate(read_frames(a.inp)):
        t = i / FPS
        for k, sc in enumerate(SCENES):
            if not (sc["t0"] <= t < sc["t1"]):
                continue
            x0, x1 = sc["x0"], sc["x1"]
            n = render_new(k, t)
            reg = fr.astype(float)
            sil = (255 - n.min(axis=2)) > 40
            sil[:, :x0] = False
            sil[:, x1:] = False
            use = sil & ~plaque_mask(k, t)
            for ex0, ex1, ey0, ey1 in sc["excl"]:
                use[ey0:ey1, ex0:ex1] = False
            u = 255 - reg.mean(axis=2)
            v = 255 - n.mean(axis=2)
            alpha = float(np.clip((u[use] * v[use]).sum() / max((v[use] ** 2).sum(), 1e-6), 0, 1)) if use.sum() > 100 else 0.0
            if a.diag:
                print(sc["name"], i, round(t, 2), "alpha", round(alpha, 3))
            elif alpha > 0.02 and t < sc["delta_until"] and alpha < 0.97:
                # delta mode: keep whatever else is visible in the frame
                t_ref = sc["ref"] / FPS
                old = resample(ref_old[k], k, t_ref, t)
                newr = resample(ref_new[k], k, t_ref, t)
                region = np.zeros((H, W), bool)
                region[:, x0:x1] = True
                m = (sil | ((255 - old.min(axis=2)) > 3)) & region
                m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 127
                soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
                out = reg + alpha * (newr - old) * soft[..., None]
                fr = np.clip(out + 0.5, 0, 255).astype(np.uint8)
            elif alpha > 0.02:
                region = np.zeros((H, W), bool)
                region[:, x0:x1] = True
                m = (sil | ((255 - reg.mean(axis=2)) > 3)) & region
                m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 127
                soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
                blend = 255 - alpha * (255 - n)
                out = reg * (1 - soft[..., None]) + blend * soft[..., None]
                fr = np.clip(out + 0.5, 0, 255).astype(np.uint8)
        if enc:
            enc.stdin.write(fr.tobytes())
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    main()
