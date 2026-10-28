"""Wykrywanie owalnej płytki na zdjęciu urny (jasny, zamknięty owal) i wektor jej rysunku do porównań. Bez scipy."""
import numpy as np
from collections import deque
from PIL import Image


def label(mask):
    H, W = mask.shape
    lab = np.zeros((H, W), dtype=np.int32)
    n = 0
    for sy in range(H):
        for sx in range(W):
            if mask[sy, sx] and not lab[sy, sx]:
                n += 1
                lab[sy, sx] = n
                q = deque([(sy, sx)])
                while q:
                    y, x = q.popleft()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n
                            q.append((yy, xx))
    return lab, n


def plaque_vec(img, is_folder, work=420):
    """Zwraca (wektor 40x50 znormalizowany, bbox) rysunku w owalnej płytce albo None."""
    im = img.convert("L")
    s = work / max(im.size)
    im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.LANCZOS)
    g = np.asarray(im, float)
    H, W = g.shape
    if is_folder:  # zestaw: urna po lewej, tekst po prawej
        col = (g < 200).mean(axis=0)
        xs = np.where(col > 0.02)[0]
        xr = int(xs[xs < 0.6 * W].max()) + 4
        g = g[:, :xr]
        H, W = g.shape
    lab, n = label(g > 225)
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if ys.min() == 0 or xs.min() == 0 or ys.max() == H - 1 or xs.max() == W - 1:
            continue  # tło dotyka brzegu
        area = len(ys)
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if not (0.004 * H * W < area < 0.2 * H * W) or not (0.5 < bw / bh < 1.3):
            continue
        if best is None or area > best[0]:
            best = (area, xs.min(), ys.min(), xs.max(), ys.max())
    if not best:
        return None
    _, x0, y0, x1, y1 = best
    c = Image.fromarray(g[y0:y1 + 1, x0:x1 + 1].astype("uint8")).resize((40, 50), Image.LANCZOS)
    v = np.asarray(c, float).ravel()
    v -= v.mean()
    return v / (np.linalg.norm(v) or 1), best[1:]
