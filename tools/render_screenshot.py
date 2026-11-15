#!/usr/bin/env python3
"""Renders docs/screenshot.png (the README and social-card image) from the game's own
tiles, font, and starter-town map: the same view the game shows at start-up.
Usage: python3 tools/render_screenshot.py"""
import pathlib, re
from PIL import Image, ImageDraw

root = pathlib.Path(__file__).resolve().parent.parent
tiles = Image.open(root / "assets/tilesets/tiles.png").convert("RGBA")
font = Image.open(root / "assets/fonts/animas_pixel.png").convert("RGBA")
fnt = (root / "assets/fonts/animas_pixel.fnt").read_text()
M = {int(a): tuple(map(int, b)) for a, *b in re.findall(r"char id=(\d+) x=(\d+) y=(\d+) width=(\d+) height=\d+ .*?xadvance=(\d+)", fnt)}
legend = {k: (int(x), int(y)) for k, x, y in re.findall(r'"(.)": Vector2i\((\d+), (\d+)\)', (root / "scripts/overworld/ascii_map.gd").read_text())}
rows = re.findall(r'^\t\t"([^"]+)",$', (root / "scenes/maps/town.gd").read_text(), re.M)[:16]

W, H, T = 240, 160, 16
img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
cx, cy = 0, 24  # camera on the player at tile (7, 6), clamped to the map
for y, row in enumerate(rows):
    for x, ch in enumerate(row):
        gx, gy = legend[ch]
        img.alpha_composite(tiles.crop((gx * T, gy * T, gx * T + T, gy * T + T)), (x * T - cx, y * T - cy))

chars = Image.open(root / "assets/characters/characters.png").convert("RGBA")
animas = Image.open(root / "assets/animas/animas.png").convert("RGBA")
ROWS = {m: i for i, m in enumerate(re.findall(r'"id": "(\w+)"', (root / "scripts/data/character_roster.gd").read_text()))}
DIR = {"down": 0, "up": 1, "left": 2, "right": 3}


def person(tx, ty, d, who):
    c = (DIR[d] * 3) * 16
    img.alpha_composite(chars.crop((c, ROWS[who] * 16, c + 16, ROWS[who] * 16 + 16)), (tx * T - cx, ty * T - cy))


person(10, 6, "down", "kid_boy"); person(9, 11, "right", "gardener"); person(7, 6, "up", "hero")

dr = ImageDraw.Draw(img)
dr.rectangle((4, 108, 235, 155), fill="#ffffff", outline="#3b3b3b", width=2)
ink = Image.new("RGBA", font.size, (32, 32, 32, 255)); ink.putalpha(font.getchannel("A"))
x = 12
for ch in "Welcome to Animas: Ember!":
    gx, gy, w, adv = M[ord(ch)]
    if w: img.alpha_composite(ink.crop((gx, gy, gx + w, gy + 9)), (x, 116))
    x += adv
x = 12
for ch in "Arrows to walk. Try the house!":
    gx, gy, w, adv = M[ord(ch)]
    if w: img.alpha_composite(ink.crop((gx, gy, gx + w, gy + 9)), (x, 128))
    x += adv
img.resize((W * 4, H * 4), Image.NEAREST).convert("RGB").save(root / "docs/screenshot.png", optimize=True)
print("wrote docs/screenshot.png")


# ---- encounter screen ----
enc = Image.new("RGBA", (W, H), (29, 26, 43, 255))
aid = 90  # Phoenyx
sp = animas.crop((((aid - 1) % 16) * 32, ((aid - 1) // 16) * 32, ((aid - 1) % 16) * 32 + 32, ((aid - 1) // 16) * 32 + 32)).resize((96, 96), Image.NEAREST)
enc.alpha_composite(sp, (72, 2))
white = Image.new("RGBA", font.size, (255, 255, 255, 255)); white.putalpha(font.getchannel("A"))
def text(im, src, msg, x, y):
    for ch in msg:
        gx, gy, w, adv = M[ord(ch)]
        if w: im.alpha_composite(src.crop((gx, gy, gx + w, gy + 9)), (x, y))
        x += adv
title = "Phoenyx   Lv 5"
text(enc, white, title, (W - sum(M[ord(c)][3] for c in title)) // 2, 98)
d2 = ImageDraw.Draw(enc)
d2.rectangle((4, 108, 235, 155), fill="#ffffff", outline="#3b3b3b", width=2)
text(enc, ink, "A wild Phoenyx appeared!", 12, 116)
text(enc, ink, "It is a Ember/Gale anima.", 12, 128)
enc.resize((W * 4, H * 4), Image.NEAREST).convert("RGB").save(root / "docs/screenshot_encounter.png", optimize=True)
print("wrote docs/screenshot_encounter.png")
