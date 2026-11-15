"""Procedural pixel-art engine for the 151 animas (used by generate_animas.py).

A sprite is built from: a body ARCHETYPE (shape), a type PALETTE, optional PATTERN
(belly / stripes / spots), FEATURES (horns, wings, flames...), an EYE style, then a
shading pass and a dark outline. Everything is deterministic from the roster data.
"""
import colorsys
import random

from PIL import Image, ImageChops, ImageDraw

S = 32
TYPE_COLOR = {
    "Ember": "#e8602c", "Tide": "#3f8fe0", "Bloom": "#58b94a", "Volt": "#f2c824",
    "Stone": "#a68a64", "Gale": "#8fc8e8", "Frost": "#9fe0ea", "Shade": "#6d4fa3",
    "Lumen": "#f4dc7a", "Venom": "#b04fb0", "Iron": "#8c98a8", "Wild": "#c9a27a",
}
INK = (30, 22, 40, 255)


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _tint(rgb, dh=0.0, ds=1.0, dv=1.0):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, min(1, s * ds), min(1, v * dv))
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def make_palette(t1, t2, rng):
    base = _tint(_rgb(TYPE_COLOR[t1]), dh=rng.uniform(-0.05, 0.05), ds=rng.uniform(0.9, 1.05))
    acc_src = _rgb(TYPE_COLOR[t2]) if t2 else _rgb(TYPE_COLOR[t1])
    acc = _tint(acc_src, dh=0.0 if t2 else rng.choice([0.09, -0.09, 0.5]), dv=0.95 if t2 else 0.85)
    belly = tuple(round(c * 0.35 + 255 * 0.65) for c in base[:3]) + (255,)
    return {
        "base": base, "light": _tint(base[:3], ds=0.85, dv=1.2), "dark": _tint(base[:3], dv=0.68),
        "acc": acc, "acc_l": _tint(acc[:3], ds=0.8, dv=1.25), "acc_d": _tint(acc[:3], dv=0.65),
        "belly": belly, "white": (250, 250, 252, 255), "black": INK,
    }


def E(d, cx, cy, rx, ry, c):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=c)


def R(d, x0, y0, x1, y1, c):
    d.rectangle((x0, y0, x1, y1), fill=c)


def P(d, pts, c):
    d.polygon(pts, fill=c)


# --------------------------------------------------------------------------- archetypes
# each draws the body onto `d` and returns anchors:
#   head (cx,cy,r)  top (x,y)  belly (cx,cy,rx,ry)  back (x,y)  tail (x,y)  wing (x,y)  face (+1/-1 side facing)
def a_blob(d, p, sc):
    rx, ry = round(11 * sc) + 2, round(9 * sc) + 2
    cy = 29 - ry - 1
    E(d, 16 - rx // 2, 29, 3, 2, p["dark"]); E(d, 16 + rx // 2, 29, 3, 2, p["dark"])
    E(d, 16, cy, rx, ry, p["base"])
    return dict(head=(16, cy - ry // 4, rx * 3 // 4), top=(16, cy - ry), belly=(16, cy + ry // 3, rx * 3 // 5, ry // 2),
                back=(16, cy - ry), tail=(16 + rx, cy + 2), wing=(16 + rx - 2, cy - 2), face=0)


def a_quad(d, p, sc):
    rx, ry, lh = round(8 * sc) + 3, round(5 * sc) + 3, round(4 * sc) + 2
    cx, cy = 14, 29 - lh - ry + 2
    for lx in (cx - rx + 1, cx - rx + 5, cx + rx - 7, cx + rx - 3):
        R(d, lx, cy + ry - 2, lx + 2, 29, p["dark"])
    E(d, cx, cy, rx, ry, p["base"])
    hr = round(5 * sc) + 3
    hx, hy = cx + rx - 1, cy - ry + 1
    E(d, hx, hy, hr, hr, p["base"]); R(d, hx + hr - 2, hy, hx + hr + 2, hy + 3, p["light"])
    return dict(head=(hx, hy, hr), top=(hx, hy - hr), belly=(cx, cy + ry // 2, rx * 2 // 3, ry // 2),
                back=(cx, cy - ry), tail=(cx - rx, cy - 1), wing=(cx - 1, cy - ry + 1), face=1)


def a_biped(d, p, sc):
    bw, bh, lh = round(6 * sc) + 3, round(6 * sc) + 3, round(4 * sc) + 2
    cy = 29 - lh - bh
    R(d, 16 - bw + 1, 29 - lh, 16 - 1, 29, p["dark"]); R(d, 16 + 1, 29 - lh, 16 + bw - 1, 29, p["dark"])
    E(d, 16, cy, bw, bh, p["base"])
    E(d, 16 - bw - 1, cy, 2, bh // 2, p["base"]); E(d, 16 + bw + 1, cy, 2, bh // 2, p["base"])
    hr = round(5 * sc) + 4
    hy = cy - bh - hr // 2 + 2
    E(d, 16, hy, hr, hr - 1, p["base"])
    return dict(head=(16, hy, hr), top=(16, hy - hr + 1), belly=(16, cy + 1, bw * 2 // 3, bh * 2 // 3),
                back=(16, cy - bh // 2), tail=(16 + bw, cy + bh // 2), wing=(16 + bw, cy - bh // 2), face=0)


def a_bird(d, p, sc):
    rx, ry = round(7 * sc) + 3, round(6 * sc) + 3
    cx, cy = 15, 29 - ry - 4
    R(d, cx - 2, cy + ry - 1, cx - 1, 29, p["acc"]); R(d, cx + 2, cy + ry - 1, cx + 3, 29, p["acc"])
    E(d, cx, cy, rx, ry, p["base"])
    hr = round(4 * sc) + 3
    hx, hy = cx + rx - 2, cy - ry + 1
    E(d, hx, hy, hr, hr, p["base"])
    P(d, [(hx + hr - 1, hy - 1), (hx + hr + 4, hy + 1), (hx + hr - 1, hy + 3)], p["acc_l"])
    E(d, cx - 1, cy + 1, rx * 2 // 3, ry // 2 + 1, p["light"])
    return dict(head=(hx, hy, hr), top=(hx, hy - hr), belly=(cx + 2, cy + ry // 2, rx // 2, ry // 2),
                back=(cx - 2, cy - ry), tail=(cx - rx, cy + 1), wing=(cx - 1, cy - 1), face=1)


def a_fish(d, p, sc):
    rx, ry = round(9 * sc) + 4, round(6 * sc) + 3
    cx, cy = 17, 16
    P(d, [(cx - rx + 1, cy), (cx - rx - 5, cy - ry), (cx - rx - 5, cy + ry)], p["acc"])
    P(d, [(cx - 3, cy - ry + 1), (cx + 3, cy - ry + 1), (cx - 1, cy - ry - 5)], p["acc"])
    E(d, cx, cy, rx, ry, p["base"])
    return dict(head=(cx + rx // 2, cy - 1, ry - 1), top=(cx + rx // 2, cy - ry), belly=(cx, cy + ry // 2, rx * 2 // 3, ry // 2),
                back=(cx - 2, cy - ry), tail=(cx - rx - 2, cy), wing=(cx - 1, cy + 1), face=1)


def a_snake(d, p, sc):
    import math
    n, r = round(8 * sc) + 5, round(3 * sc) + 2
    pts = []
    for i in range(n):
        t = i / (n - 1)
        pts.append((round(5 + 22 * t), round(22 - 9 * math.sin(t * math.pi * 1.7) * (0.5 + 0.5 * t))))
    for i, (x, y) in enumerate(pts):
        rr = max(2, round(r * (0.55 + 0.45 * i / (n - 1)))) if i < n - 1 else r + 2
        E(d, x, y, rr, rr, p["base"] if i % 2 == 0 else p["light"])
    hx, hy = pts[-1]
    return dict(head=(hx, hy, r + 2), top=(hx, hy - r - 2), belly=(pts[n // 2][0], pts[n // 2][1], 3, 2),
                back=pts[n // 2], tail=pts[0], wing=pts[n // 2 + 1], face=1)


def a_bug(d, p, sc):
    ab, th, hr = round(6 * sc) + 3, round(4 * sc) + 2, round(3 * sc) + 3
    cx, cy = 14, 29 - ab - 3
    for i in range(3):
        x = cx - 2 + i * 4
        d.line((x, cy + 2, x - 2, 28), fill=p["dark"]); d.line((x, cy + 2, x + 2, 28), fill=p["dark"])
    E(d, cx - ab // 2, cy, ab, ab - 1, p["base"])
    E(d, cx + ab - 2, cy - 1, th, th, p["light"])
    hx, hy = cx + ab + th - 2, cy - 2
    E(d, hx, hy, hr, hr, p["base"])
    d.line((hx, hy - hr, hx - 3, hy - hr - 5), fill=p["acc_d"]); d.line((hx + 1, hy - hr, hx + 4, hy - hr - 5), fill=p["acc_d"])
    return dict(head=(hx, hy, hr), top=(hx, hy - hr), belly=(cx - 2, cy + 1, ab * 2 // 3, ab // 2),
                back=(cx - 2, cy - ab), tail=(cx - ab * 3 // 2, cy), wing=(cx + 2, cy - th), face=1)


def a_plant(d, p, sc):
    br, hr = round(6 * sc) + 4, round(4 * sc) + 3
    cy = 29 - br
    R(d, 15, cy - br - 3, 17, cy - 2, p["acc_d"])
    E(d, 10, cy - br // 2, 4, 2, p["acc"]); E(d, 22, cy - br // 2, 4, 2, p["acc"])
    E(d, 16, cy, br, br - 1, p["base"])
    hy = cy - br - hr + 1
    for a in range(0, 360, 60):
        import math
        E(d, 16 + round(math.cos(math.radians(a)) * (hr + 1)), hy + round(math.sin(math.radians(a)) * (hr + 1)), 3, 3, p["acc_l"])
    E(d, 16, hy, hr - 1, hr - 1, p["base"])
    return dict(head=(16, cy - 1, br - 1), top=(16, hy - hr - 3), belly=(16, cy + 3, br // 2, br // 3),
                back=(16, cy - br), tail=(16 + br, cy + 3), wing=(16 + br, cy - 2), face=0, flower=(16, hy, hr))


def a_golem(d, p, sc):
    w, h, lh = round(5 * sc) + 4, round(6 * sc) + 4, round(3 * sc) + 2
    cy = 29 - lh - h
    R(d, 16 - w, 29 - lh, 16 - 2, 29, p["dark"]); R(d, 16 + 2, 29 - lh, 16 + w, 29, p["dark"])
    R(d, 16 - w - 4, cy - h // 2, 16 - w, cy + h // 2 + 2, p["light"]); R(d, 16 + w, cy - h // 2, 16 + w + 4, cy + h // 2 + 2, p["light"])
    R(d, 16 - w, cy - h, 16 + w, cy + h, p["base"])
    hh = round(4 * sc) + 3
    R(d, 16 - hh - 1, cy - h - hh * 2 + 2, 16 + hh + 1, cy - h + 1, p["light"])
    return dict(head=(16, cy - h - hh + 2, hh + 1), top=(16, cy - h - hh * 2 + 2), belly=(16, cy + 2, w - 2, h - 3),
                back=(16, cy - h), tail=(16 + w, cy + h // 2), wing=(16 + w + 3, cy - h // 2), face=0)


def a_ghost(d, p, sc):
    r, bh = round(7 * sc) + 4, round(7 * sc) + 3
    cy = 8 + r
    E(d, 16, cy, r, r, p["base"]); R(d, 16 - r, cy, 16 + r, cy + bh, p["base"])
    for i in range(4):
        E(d, 16 - r + 2 + i * (r // 2 + 1), cy + bh, r // 4 + 2, 3, p["base"])
    E(d, 16 - r - 1, cy + 3, 2, 3, p["light"]); E(d, 16 + r + 1, cy + 3, 2, 3, p["light"])
    return dict(head=(16, cy - 1, r), top=(16, cy - r), belly=(16, cy + bh // 2, r // 2, bh // 2),
                back=(16, cy - r), tail=(16 + r, cy + bh), wing=(16 + r, cy), face=0)


def a_dragon(d, p, sc):
    rx, ry = round(8 * sc) + 4, round(5 * sc) + 3
    cx, cy = 14, 29 - ry - 4
    P(d, [(cx - rx + 2, cy - 1), (cx - rx - 8, cy + ry + 1), (cx - rx + 1, cy + ry - 1)], p["base"])
    for lx in (cx - 3, cx + 3):
        R(d, lx, cy + ry - 2, lx + 2, 29, p["dark"])
    E(d, cx, cy, rx, ry, p["base"])
    hr = round(4 * sc) + 3
    hx, hy = cx + rx, cy - ry - 1
    R(d, cx + rx - 5, cy - ry, cx + rx - 1, cy, p["base"])
    E(d, hx, hy, hr, hr - 1, p["base"]); R(d, hx + hr - 2, hy, hx + hr + 3, hy + 3, p["light"])
    return dict(head=(hx, hy, hr), top=(hx, hy - hr + 1), belly=(cx, cy + ry // 2, rx * 2 // 3, ry // 2),
                back=(cx, cy - ry), tail=(cx - rx - 6, cy + ry - 1), wing=(cx - 1, cy - ry + 1), face=1)


def a_crab(d, p, sc):
    rx, ry = round(8 * sc) + 5, round(5 * sc) + 3
    cx, cy = 16, 29 - ry - 2
    for i in range(3):
        d.line((cx - rx + 2 + i * 2, cy + ry - 2, cx - rx - 1 + i, 29), fill=p["dark"])
        d.line((cx + rx - 2 - i * 2, cy + ry - 2, cx + rx + 1 - i, 29), fill=p["dark"])
    for sx in (-1, 1):
        E(d, cx + sx * (rx + 2), cy - ry - 1, 4, 4, p["acc"])
        P(d, [(cx + sx * (rx + 2), cy - ry - 5), (cx + sx * (rx + 5), cy - ry - 3), (cx + sx * (rx + 2), cy - ry - 1)], (0, 0, 0, 0))
        d.line((cx + sx * (rx - 1), cy - 2, cx + sx * (rx + 1), cy - ry), fill=p["acc"], width=2)
    E(d, cx, cy, rx, ry, p["base"])
    return dict(head=(cx, cy - 1, rx - 1), top=(cx, cy - ry), belly=(cx, cy + ry // 2, rx // 2, ry // 3),
                back=(cx, cy - ry), tail=(cx + rx, cy + 1), wing=(cx + rx, cy - 3), face=0)


def a_bat(d, p, sc):
    br, wr = round(4 * sc) + 4, round(9 * sc) + 5
    cx, cy = 16, 18
    for sx in (-1, 1):
        P(d, [(cx + sx * 2, cy - 2), (cx + sx * wr, cy - 9), (cx + sx * (wr - 2), cy + 1), (cx + sx * (wr // 2), cy + 5), (cx + sx * 3, cy + 5)], p["acc"])
    E(d, cx, cy, br, br + 1, p["base"])
    E(d, cx, cy - br, br - 1, br - 1, p["base"])
    return dict(head=(cx, cy - br, br - 1), top=(cx, cy - br * 2 + 1), belly=(cx, cy + 1, br - 1, br - 1),
                back=(cx, cy - 3), tail=(cx + 3, cy + br + 2), wing=(cx + 3, cy - 3), face=0, bat=True)


def a_orb(d, p, sc):
    r = round(9 * sc) + 4
    cy = 17
    E(d, 16, 29, r - 2, 2, p["dark"])
    E(d, 16, cy, r, r, p["base"])
    E(d, 16 - r, cy + 1, 3, 3, p["light"]); E(d, 16 + r, cy + 1, 3, 3, p["light"])
    return dict(head=(16, cy, r), top=(16, cy - r), belly=(16, cy + r // 3, r // 2, r // 2),
                back=(16, cy - r), tail=(16 + r, cy + 2), wing=(16 + r - 1, cy - 2), face=0)


ARCH = {"blob": a_blob, "quad": a_quad, "biped": a_biped, "bird": a_bird, "fish": a_fish, "snake": a_snake, "bug": a_bug,
        "plant": a_plant, "golem": a_golem, "ghost": a_ghost, "dragon": a_dragon, "crab": a_crab, "bat": a_bat, "orb": a_orb}

# --------------------------------------------------------------------------- features
BEHIND = {"mane", "wings", "tail_flame", "tail_leaf", "tail_bolt", "tail_fin", "tail_tuft", "spikes"}


def f_mane(d, p, a, sc):
    hx, hy, r = a["head"]
    E(d, hx - a["face"], hy, r + 3, r + 3, p["acc"])


def f_wings(d, p, a, sc):
    x, y = a["wing"]
    s = 5 + round(5 * sc)
    for sx in ((-1, 1) if a.get("bat") or a["face"] == 0 else (-1,)):
        P(d, [(x, y), (x + sx * s, y - s - 2), (x + sx * (s + 3), y - 1), (x + sx * (s // 2), y + 3)], p["acc_l"])
    if a["face"] != 0 and not a.get("bat"):
        P(d, [(x, y), (x - 2, y - s - 3), (x + 4, y - s + 1), (x + 5, y + 1)], p["acc_l"])


def f_tail_flame(d, p, a, sc):
    x, y = a["tail"]
    s = 3 + round(3 * sc)
    sx = -1 if a["face"] >= 0 else 1
    P(d, [(x, y + 2), (x + sx * s, y - s - 1), (x + sx * (s + 2), y + 1), (x + sx * 2, y + 4)], (232, 90, 40, 255))
    P(d, [(x + sx, y + 1), (x + sx * s, y - s + 2), (x + sx * (s + 1), y + 1)], (250, 205, 70, 255))


def f_tail_leaf(d, p, a, sc):
    x, y = a["tail"]
    sx = -1 if a["face"] >= 0 else 1
    s = 4 + round(4 * sc)
    P(d, [(x, y), (x + sx * s, y - s), (x + sx * (s + 3), y - s // 2), (x + sx * 2, y + 3)], (88, 180, 80, 255))
    d.line((x, y, x + sx * s, y - s + 1), fill=(48, 120, 56, 255))


def f_tail_bolt(d, p, a, sc):
    x, y = a["tail"]
    sx = -1 if a["face"] >= 0 else 1
    s = 3 + round(3 * sc)
    P(d, [(x, y), (x + sx * s, y - s), (x + sx * (s - 2), y - s + 2), (x + sx * (s + 3), y - s * 2), (x + sx * 2, y - s + 3), (x + sx * 4, y - s + 1), (x + sx * 1, y + 2)], (250, 214, 40, 255))


def f_tail_fin(d, p, a, sc):
    x, y = a["tail"]
    sx = -1 if a["face"] >= 0 else 1
    s = 4 + round(3 * sc)
    P(d, [(x + sx, y - 1), (x + sx * (s + 2), y - s), (x + sx * (s + 2), y + s - 2)], p["acc"])


def f_tail_tuft(d, p, a, sc):
    x, y = a["tail"]
    sx = -1 if a["face"] >= 0 else 1
    E(d, x + sx * 2, y, 3 + round(2 * sc), 3 + round(2 * sc), p["acc_l"])


def f_spikes(d, p, a, sc):
    x, y = a["back"]
    n = 3 + round(2 * sc)
    for i in range(n):
        px = x - 6 + i * 4
        P(d, [(px, y + 1), (px + 2, y - 4 - round(2 * sc)), (px + 4, y + 1)], p["acc_d"])


def f_horn(d, p, a, sc):
    hx, hy, r = a["head"]
    s = 3 + round(3 * sc)
    for sx in (-1, 1):
        P(d, [(hx + sx * (r // 2) - 2, hy - r + 2), (hx + sx * (r // 2 + 2), hy - r - s), (hx + sx * (r // 2) + 2, hy - r + 2)], p["white"])


def f_ears(d, p, a, sc):
    hx, hy, r = a["head"]
    s = 3 + round(2 * sc)
    for sx in (-1, 1):
        P(d, [(hx + sx * (r - 1) - 2, hy - r + 3), (hx + sx * (r - 2), hy - r - s), (hx + sx * (r - 1) + 3, hy - r + 3)], p["base"])
        P(d, [(hx + sx * (r - 2), hy - r + 2), (hx + sx * (r - 2), hy - r - s + 3), (hx + sx * (r - 2) + 1, hy - r + 2)], p["acc_l"])


def f_longears(d, p, a, sc):
    hx, hy, r = a["head"]
    s = 5 + round(4 * sc)
    for sx in (-1, 1):
        R(d, hx + sx * (r // 2) - 1, hy - r - s, hx + sx * (r // 2) + 1, hy - r + 3, p["base"])
        R(d, hx + sx * (r // 2), hy - r - s + 1, hx + sx * (r // 2), hy - r + 1, p["acc_l"])


def f_crest(d, p, a, sc):
    x, y = a["top"]
    for i, dx in enumerate((-3, 0, 3)):
        h = 4 + round(3 * sc) - (i == 0 or i == 2)
        P(d, [(x + dx - 2, y + 2), (x + dx, y - h), (x + dx + 2, y + 2)], p["acc"])


def f_flamehead(d, p, a, sc):
    x, y = a["top"]
    s = 4 + round(4 * sc)
    P(d, [(x - 4, y + 2), (x - 3, y - s // 2), (x - 1, y - s + 2), (x, y - s - 3), (x + 2, y - s), (x + 4, y - s // 2), (x + 5, y + 2)], (232, 90, 40, 255))
    P(d, [(x - 2, y + 1), (x, y - s + 1), (x + 3, y + 1)], (250, 205, 70, 255))


def f_halo(d, p, a, sc):
    x, y = a["top"]
    d.ellipse((x - 6, y - 8, x + 6, y - 3), outline=(250, 220, 90, 255), width=1)


def f_fangs(d, p, a, sc):
    hx, hy, r = a["head"]
    my = hy + r // 2
    for sx in (-1, 1):
        P(d, [(hx + sx * 2 - 1 + r // 3 * a["face"], my), (hx + sx * 2 + r // 3 * a["face"], my + 3), (hx + sx * 2 + 1 + r // 3 * a["face"], my)], p["white"])


def f_shell(d, p, a, sc):
    x, y = a["back"]
    r = 5 + round(3 * sc)
    d.pieslice((x - r, y - r // 2 - 1, x + r, y + r + 2), 180, 360, fill=p["acc"])
    d.line((x, y - r // 2, x, y + 1), fill=p["acc_d"]); d.line((x - r // 2, y - r // 3, x - r // 3, y + 1), fill=p["acc_d"]); d.line((x + r // 2, y - r // 3, x + r // 3, y + 1), fill=p["acc_d"])


def f_whiskers(d, p, a, sc):
    hx, hy, r = a["head"]
    for sx in (-1, 1):
        d.line((hx + sx * (r - 1), hy + 2, hx + sx * (r + 3), hy + 1), fill=p["white"]); d.line((hx + sx * (r - 1), hy + 3, hx + sx * (r + 3), hy + 4), fill=p["white"])


FEAT = {k[2:]: v for k, v in globals().items() if k.startswith("f_")}
# --------------------------------------------------------------------------- patterns


def pat_belly(d, p, a, rng):
    cx, cy, rx, ry = a["belly"]
    E(d, cx, cy, max(2, rx), max(2, ry), p["belly"])


def pat_stripes(d, p, a, rng):
    cx, cy, _, _ = a["belly"]
    for i in range(-2, 4):
        d.line((cx - 12 + i * 4, cy - 12, cx - 4 + i * 4, cy + 10), fill=p["dark"], width=2)


def pat_spots(d, p, a, rng):
    cx, cy, rx, ry = a["belly"]
    for _ in range(5):
        x, y = cx + rng.randint(-9, 9), cy + rng.randint(-9, 6)
        E(d, x, y, 1 + rng.randint(0, 1), 1 + rng.randint(0, 1), p["acc_d"])


PATTERN = {"belly": pat_belly, "stripes": pat_stripes, "spots": pat_spots}
# --------------------------------------------------------------------------- compose
PAD, W = 10, S + 20  # working canvas: art is drawn with an offset, then auto-fitted into 32x32


class OD:
    """ImageDraw wrapper that shifts every coordinate by a fixed offset."""

    def __init__(self, im, o=PAD):
        self.d, self.o = ImageDraw.Draw(im), o

    def _xy(self, xy):
        o = self.o
        if isinstance(xy[0], (tuple, list)):
            return [(p[0] + o, p[1] + o) for p in xy]
        return [v + o for v in xy]

    def ellipse(self, xy, **k): self.d.ellipse(self._xy(xy), **k)
    def rectangle(self, xy, **k): self.d.rectangle(self._xy(xy), **k)
    def polygon(self, xy, **k): self.d.polygon(self._xy(xy), **k)
    def line(self, xy, **k): self.d.line(self._xy(xy), **k)
    def pieslice(self, xy, a, b, **k): self.d.pieslice(self._xy(xy), a, b, **k)
    def point(self, xy, **k): self.d.point(self._xy(xy), **k)


def _draw_once(spec, feats, scale, seed):
    rng = random.Random(seed)
    t1, t2 = spec["types"][0], (spec["types"][1] if len(spec["types"]) > 1 else None)
    p = make_palette(t1, t2, rng)
    back, body, pat, front = (Image.new("RGBA", (W, W), (0, 0, 0, 0)) for _ in range(4))
    a = ARCH[spec["arch"]](OD(body), p, scale)
    for f in feats:
        if f in BEHIND:
            FEAT[f](OD(back), p, a, scale)
    if spec.get("pattern"):
        for name in spec["pattern"].split("+"):
            PATTERN[name](OD(pat), p, a, rng)
        pat.putalpha(ImageChops.multiply(pat.getchannel("A"), body.getchannel("A")))
    if "flower" in a:
        fx, fy, fr = a["flower"]
        E(OD(front), fx, fy, max(2, fr - 3), max(2, fr - 3), p["acc"])
    for f in feats:
        if f not in BEHIND:
            FEAT[f](OD(front), p, a, scale)
    img = Image.alpha_composite(Image.alpha_composite(back, body), Image.alpha_composite(pat, front))
    px, out = img.load(), img.copy()
    po = out.load()
    for y in range(W):
        for x in range(W):
            c = px[x, y]
            if c[3] == 0 or c == p["white"]:
                continue
            tl = px[x - 1, y - 1][3] == 0 if x > 0 and y > 0 else True
            br = (px[x + 1, y + 1][3] == 0 if x < W - 1 and y < W - 1 else True) or (px[x, y + 1][3] == 0 if y < W - 1 else True)
            if br:
                po[x, y] = _tint(c[:3], dv=0.78)
            elif tl:
                po[x, y] = _tint(c[:3], ds=0.9, dv=1.18)
    img, px = out, out.load()
    ol = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    po = ol.load()
    ink = tuple(round(c * 0.45) for c in p["dark"][:3]) + (255,)
    for y in range(W):
        for x in range(W):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < W and px[nx, ny][3] > 0:
                        po[x, y] = ink
                        break
    img = Image.alpha_composite(ol, img)
    eyes(img, a, p, spec.get("eye", "dot"))
    return img


def eyes(img, a, p, style):
    hx, hy, r = a["head"]
    d = OD(img)
    face = a["face"]
    gap = max(2, round(r * 0.45))
    ey = hy - max(0, r // 6)
    xs = (hx - gap + face * 2, hx + gap + face * 2) if face == 0 else (hx + face * 1 - gap // 2 + 1, hx + face * (gap + 2))
    for x in xs:
        if style == "dot":
            R(d, x - 1, ey - 1, x, ey, p["black"]); d.point((x - 1, ey - 1), fill=p["white"])
        elif style == "round":
            R(d, x - 1, ey - 1, x + 1, ey + 1, p["white"]); d.point((x + (1 if face >= 0 else 0), ey), fill=p["black"]); d.point((x + (1 if face >= 0 else 0), ey + 1), fill=p["black"])
        elif style == "angry":
            R(d, x - 1, ey, x, ey + 1, p["black"]); d.line((x - 2, ey - 2 + (x > hx), x + 1, ey - 1 - (x > hx)), fill=p["black"])
        elif style == "sleepy":
            d.line((x - 1, ey, x + 1, ey), fill=p["black"])
        elif style == "big":
            R(d, x - 1, ey - 2, x + 1, ey + 1, p["black"]); d.point((x - 1, ey - 2), fill=p["white"]); d.point((x, ey - 2), fill=p["white"])
        elif style == "glow":
            R(d, x - 1, ey - 1, x, ey, (255, 240, 120, 255))
    if style in ("round", "dot", "big") and a["face"] == 0:
        d.point((hx, ey + max(2, r // 3)), fill=p["black"])


def render(spec, feats, scale, seed, limit=30):
    """Draws the anima, shrinking it until the whole sprite (with features) fits in 32x32."""
    sc = scale
    for _ in range(8):
        big = _draw_once(spec, feats, sc, seed)
        bb = big.getbbox()
        if bb and (bb[2] - bb[0] <= limit and bb[3] - bb[1] <= limit):
            break
        sc -= 0.06
    spr = big.crop(bb)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(spr, ((S - spr.width) // 2, S - 1 - spr.height))
    return out
