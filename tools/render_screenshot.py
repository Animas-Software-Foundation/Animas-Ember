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

def person(tx, ty, d, body, hair):
    dr, ox, oy = ImageDraw.Draw(img), tx * T - cx, ty * T - cy
    r = lambda x, y, w, h, c: dr.rectangle((ox + x, oy + y, ox + x + w - 1, oy + y + h - 1), fill=c)
    r(4, 13, 3, 3, "#2a2a30"); r(9, 13, 3, 3, "#2a2a30"); r(3, 7, 10, 6, body)
    r(4, 1, 8, 7, "#f0c8a0"); r(4, 0, 8, 7 if d == "up" else 3, hair)
    if d == "down": r(5, 5, 1, 2, "#222"); r(10, 5, 1, 2, "#222")
    if d == "left": r(5, 5, 1, 2, "#222")
    if d == "right": r(10, 5, 1, 2, "#222")

person(10, 6, "down", "#4a7bd0", "#3a2a1a"); person(9, 11, "right", "#d0884a", "#222222"); person(7, 6, "up", "#d04a4a", "#2a2a5a")

dr = ImageDraw.Draw(img)
dr.rectangle((4, 108, 235, 155), fill="#ffffff", outline="#3b3b3b", width=2)
ink = Image.new("RGBA", font.size, (32, 32, 32, 255)); ink.putalpha(font.getchannel("A"))
x = 12
for ch in "Welcome to Animas: Ember!":
    gx, gy, w, adv = M[ord(ch)]
    if w: img.alpha_composite(ink.crop((gx, gy, gx + w, gy + 9)), (x, 116))
    x += adv
x = 12
for ch in "Walk with the arrow keys. Try the house!":
    gx, gy, w, adv = M[ord(ch)]
    if w: img.alpha_composite(ink.crop((gx, gy, gx + w, gy + 9)), (x, 128))
    x += adv
img.resize((W * 4, H * 4), Image.NEAREST).convert("RGB").save(root / "docs/screenshot.png", optimize=True)
print("wrote docs/screenshot.png")
