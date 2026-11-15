#!/usr/bin/env python3
"""Generates the hero, rival, NPC, and trainer sprites, each with a unique look.

Outputs (relative to the project root):
  assets/characters/characters.png   192x(16*N): one row per character, 12 frames of 16x16
                                     frame order: down, up, left, right x (idle, walkA, walkB)
  scripts/data/character_roster.gd   roster data (do not edit by hand)
  docs/assets/characters.png, docs/characters_preview.png

Usage:  pip install pillow && python3 tools/generate_characters.py
Add or change a character by editing LOOKS below and re-running.
"""
import json
import os
import shutil

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKIN = {"fair": "#f6d2b0", "light": "#e8b98f", "tan": "#d19a6e", "brown": "#a8734a", "deep": "#7a4f32", "dark": "#5a3825"}
HAIR = {"black": "#2a2330", "brown": "#6a4128", "chestnut": "#8a5230", "blond": "#e8c458", "red": "#c8452c", "silver": "#c8ccd8", "white": "#f0f0f4",
        "pink": "#e878a8", "teal": "#3fb0a8", "purple": "#7a52b8", "gray": "#8a8a96", "yellow": "#f4d838"}
INK = (34, 26, 44, 255)


def C(h):
    h = SKIN.get(h) or HAIR.get(h) or h
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    return tuple(min(255, round(x * f)) for x in c[:3]) + (255,)


# id, name, role, skin, hair style, hair color, outfit, color1, color2, pants, accessory, accessory color
LOOKS = [
    ("hero", "Hero", "Player", "tan", "spiky", "brown", "jacket", "#e8742c", "#f8e8c8", "#3a4a7a", "goggles", "#f4c838"),
    ("rival", "Kade", "Rival", "light", "spiky", "silver", "jacket", "#2a3a5a", "#3fb0a8", "#22222e", "scarf", "#3fb0a8"),
    ("mom", "Mom", "Family", "light", "long", "chestnut", "dress", "#f0c860", "#ffffff", "#f0c860", "none", "#ffffff"),
    ("elder", "Elder Ashgrove", "Elder", "tan", "bald", "white", "robe", "#4a8a56", "#e8d890", "#4a8a56", "beard", "#f0f0f4"),
    ("professor", "Prof. Cinder", "Professor", "light", "messy", "gray", "jacket", "#f4f4f8", "#c8452c", "#3a3a4a", "glasses", "#222230"),
    ("shopkeeper", "Marta", "Shopkeeper", "brown", "bun", "black", "apron", "#4a78c8", "#f4f4f8", "#4a78c8", "none", "#ffffff"),
    ("healer", "Healer Wren", "Healer", "fair", "bob", "teal", "uniform", "#f4f4f8", "#e878a8", "#f4f4f8", "headband", "#e878a8"),
    ("kid_boy", "Pip", "Villager", "light", "short", "chestnut", "tee", "#f08a24", "#ffffff", "#4a5a8a", "none", "#ffffff"),
    ("kid_girl", "Lila", "Villager", "tan", "ponytail", "purple", "tee", "#a868d8", "#ffffff", "#ece4f4", "bow", "#f4d838"),
    ("fisher", "Old Finn", "Fisher", "light", "short", "gray", "jacket", "#3a6aa8", "#f4d838", "#6a5a3a", "hat", "#f4d838"),
    ("baker", "Bram", "Baker", "brown", "bald", "black", "apron", "#c8452c", "#f4f4f8", "#7a6a5a", "none", "#ffffff"),
    ("guard", "Sgt. Holt", "Guard", "deep", "short", "black", "uniform", "#2a4078", "#f4d838", "#22305a", "cap", "#2a4078"),
    ("gardener", "Flora", "Gardener", "tan", "ponytail", "blond", "overalls", "#58a84a", "#f4f4f8", "#58a84a", "hat", "#e8d890"),
    ("miner", "Dug", "Miner", "brown", "short", "brown", "overalls", "#8a8a96", "#c8452c", "#6a6a76", "cap", "#f4c838"),
    ("student", "Tobi", "Student", "light", "short", "black", "tee", "#58a84a", "#ffffff", "#3a3a4a", "backpack", "#c8452c"),
    ("artist", "Sable", "Artist", "fair", "long", "black", "poncho", "#3fb0a8", "#f4d838", "#3a3a4a", "cap", "#7a52b8"),
    ("sailor", "Kai", "Sailor", "deep", "short", "black", "uniform", "#f4f4f8", "#2a4078", "#2a4078", "headband", "#f4f4f8"),
    ("granny", "Granny Pearl", "Villager", "fair", "bun", "silver", "dress", "#b8a0d8", "#f4f4f8", "#b8a0d8", "glasses", "#8a6a3a"),
    ("merchant", "Zed", "Merchant", "tan", "bald", "black", "poncho", "#c8452c", "#f4c838", "#4a3a2a", "beard", "#2a2330"),
    ("musician", "Lyra", "Musician", "light", "long", "pink", "dress", "#7a52b8", "#f4d838", "#7a52b8", "bow", "#f4d838"),
    ("scout", "Scout Nell", "Trainer", "tan", "bob", "red", "jacket", "#58a84a", "#e8d890", "#4a5a3a", "cap", "#58a84a"),
    ("camper", "Camper Ty", "Trainer", "light", "short", "brown", "tee", "#d8c890", "#c8452c", "#4a6a8a", "headband", "#c8452c"),
    ("angler", "Angler Rosa", "Trainer", "brown", "ponytail", "black", "overalls", "#3a8ac8", "#f4f4f8", "#3a8ac8", "hat", "#e8d890"),
    ("hiker", "Hiker Rufus", "Trainer", "tan", "short", "brown", "jacket", "#8a5a3a", "#f08a24", "#4a4a3a", "backpack", "#c8452c"),
    ("cadet", "Cadet Vega", "Trainer", "fair", "short", "silver", "uniform", "#2a4078", "#c8ccd8", "#22305a", "glasses", "#222230"),
    ("mystic", "Mystic Orin", "Trainer", "light", "long", "white", "robe", "#6a3ea8", "#f4d838", "#6a3ea8", "beard", "#f0f0f4"),
    ("sparkler", "Sparkler Zia", "Trainer", "tan", "spiky", "yellow", "jacket", "#f4d838", "#2a2330", "#3a3a4a", "goggles", "#3fb0a8"),
    ("brawler", "Brawler Gunnar", "Trainer", "fair", "mohawk", "red", "tee", "#2a2330", "#c8452c", "#4a4a5a", "headband", "#c8452c"),
    ("netter", "Netter Pim", "Trainer", "brown", "short", "black", "tee", "#58a84a", "#ffffff", "#7a6a3a", "hat", "#e8d890"),
    ("swimmer", "Swimmer Coral", "Trainer", "light", "bob", "teal", "uniform", "#3fb0d8", "#f4f4f8", "#3fb0d8", "none", "#ffffff"),
    ("warden", "Warden Solara", "Boss", "deep", "afro", "red", "poncho", "#c8452c", "#f4c838", "#3a2a2a", "goggles", "#f4c838"),
]
FRAMES = 12


def draw_char(look, d, f):
    """Returns a 16x16 RGBA frame. d: 0 down, 1 up, 2 left, 3 right; f: 0 idle, 1/2 walk."""
    _, _, _, skin, hs, hc, outfit, c1, c2, pants, acc, ac = look
    skin, hair, c1, c2, pants, ac = C(skin), C(hc), C(c1), C(c2), C(pants), C(ac)
    left = d == 2 or d == 3
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    R = lambda x0, y0, x1, y1, c: g.rectangle((x0, y0, x1, y1), fill=c)
    if d == 3:
        d = 2
        mirror = True
    else:
        mirror = False
    bob = 0
    # legs (hidden by robes)
    if outfit != "robe":
        lw = 0 if f != 1 else 1
        rw = 0 if f != 2 else 1
        if left:
            R(6, 12 + lw, 9, 14, pants) if f == 0 else (R(5, 12, 7, 14 - (f == 2), pants), R(8, 12, 10, 14 - (f == 1), pants))
            R(6, 14, 9, 14, shade(pants, .6)) if f == 0 else None
        else:
            R(5, 12 + lw, 6, 14, pants); R(9, 12 + rw, 10, 14, pants)
            R(5, 14, 6, 14, shade(pants, .6)); R(9, 14, 10, 14, shade(pants, .6))
    # body
    body_top = 8
    if outfit == "dress":
        R(4, body_top, 11, 11, c1); R(3, 12, 12, 13, c1); R(5, 11, 10, 11, c2)
    elif outfit == "robe":
        R(4, body_top, 11, 14, c1); R(3, 12, 12, 14, c1); R(3, 14, 12, 14, c2)
        if not left:
            R(7, body_top, 8, 14, c2)
    elif outfit == "poncho":
        R(3, body_top, 12, 11, c1); R(3, 11, 12, 11, c2); R(5, 12, 10, 12, shade(c1, .8))
    else:
        R(4, body_top, 11, 11, c1)
        if outfit == "jacket":
            R(7, body_top, 8, 11, c2) if not left else None
            R(5, body_top, 10, body_top, c2)
        elif outfit == "apron":
            R(5, 9, 10, 12, c2) if not left else R(6, 9, 9, 12, c2)
        elif outfit == "overalls":
            R(4, body_top, 11, 9, c2); R(5, 10, 10, 12, c1); R(5, body_top, 5, 9, c1); R(10, body_top, 10, 9, c1)
        elif outfit == "uniform":
            R(4, 11, 11, 11, c2); R(7, body_top, 8, 10, c2) if not left else R(6, 9, 6, 9, c2)
        elif outfit == "tee":
            R(5, body_top, 10, body_top, c2) if d == 0 else None
    # arms
    ar = c1 if outfit not in ("tee", "dress") else skin
    if left:
        R(6, 9, 8, 11 + (f == 1), c1 if outfit != "tee" else skin) if False else R(6, 9 - (f == 2), 8, 11, c1 if outfit not in ("tee",) else c1)
        R(6, 11, 8, 11, skin)
    else:
        R(3, 9 + (f == 1), 3, 11, c1 if outfit != "poncho" else c1); R(12, 9 + (f == 2), 12, 11, c1)
        R(3, 11 + (f == 1), 3, 11 + (f == 1), skin); R(12, 11 + (f == 2), 12, 11 + (f == 2), skin)
    if outfit in ("tee", "dress") and not left:
        R(3, 11, 3, 11, skin); R(12, 11, 12, 11, skin)
    # backpack
    if acc == "backpack":
        if d == 1:
            R(4, 8, 11, 12, ac); R(5, 9, 10, 9, shade(ac, .7))
        elif left:
            R(10, 8, 12, 11, ac)
    if acc == "scarf":
        R(4, 8, 11, 8, ac)
        if not left:
            R(10, 9, 11, 11, ac)
    # head
    R(4, 2, 11, 7, skin)
    if left:
        R(3, 5, 3, 6, skin) if False else None
    # hair
    back_all = d == 1
    h = hair
    if hs == "short":
        R(4, 1, 11, 3, h)
        R(4, 4, 4, 4, h); R(11, 4, 11, 4, h)
    elif hs == "spiky":
        R(4, 2, 11, 3, h)
        for x in (4, 6, 8, 10):
            R(x, 1, x + 1, 1, h)
        R(4, 4, 4, 4, h); R(11, 4, 11, 4, h)
    elif hs == "messy":
        R(3, 2, 12, 3, h); R(4, 1, 6, 1, h); R(9, 1, 11, 1, h); R(3, 4, 4, 5, h); R(11, 4, 12, 5, h)
    elif hs == "long":
        R(4, 1, 11, 3, h); R(3, 2, 4, 9, h); R(11, 2, 12, 9, h)
    elif hs == "bob":
        R(4, 1, 11, 3, h); R(3, 2, 4, 6, h); R(11, 2, 12, 6, h)
    elif hs == "ponytail":
        R(4, 1, 11, 3, h); R(4, 4, 4, 4, h); R(11, 4, 11, 4, h)
        R(12, 3, 13, 7, h) if not left else R(11, 3, 12, 7, h)
    elif hs == "bun":
        R(4, 1, 11, 3, h); R(6, 0, 9, 1, h); R(4, 4, 4, 4, h); R(11, 4, 11, 4, h)
    elif hs == "mohawk":
        R(7, 0, 8, 3, h); R(4, 3, 11, 3, shade(h, .6)) if False else None
    elif hs == "afro":
        R(3, 0, 12, 4, h); R(2, 2, 13, 6, h)
    if back_all and hs != "bald":
        R(4, 1, 11, 7, h)
        if hs == "long":
            R(3, 2, 12, 10, h)
        if hs == "afro":
            R(2, 0, 13, 7, h)
        if hs == "bob":
            R(3, 2, 12, 7, h)
    elif left and hs in ("long", "bob", "ponytail", "afro", "messy"):
        R(8 if hs != "afro" else 9, 3, 11, 7 if hs != "long" else 9, h)
    elif left and hs in ("short", "spiky", "bun"):
        R(8, 3, 11, 4, h)
    # face
    if not back_all:
        if d == 0:
            R(5, 5, 5, 5, INK); R(10, 5, 10, 5, INK)
            R(5, 7, 5, 7, shade(skin, .9)) if False else None
        else:
            R(4, 5, 4, 5, INK)
            R(3, 6, 3, 6, skin)
    # hats and accessories on the head
    if acc == "glasses" and not back_all:
        if d == 0:
            R(4, 5, 6, 5, ac); R(9, 5, 11, 5, ac); R(7, 5, 8, 5, ac)
        else:
            R(3, 5, 5, 5, ac)
    if acc == "goggles":
        R(4, 2, 11, 2, ac); R(5, 3, 6, 3, shade(ac, 1.2)) if d == 0 else None
        if d == 0:
            R(9, 3, 10, 3, shade(ac, 1.2))
    if acc == "headband":
        R(4, 3, 11, 3, ac)
    if acc == "cap":
        R(4, 1, 11, 3, ac)
        if d == 0:
            R(3, 3, 12, 3, shade(ac, .75))
        elif left:
            R(2, 3, 6, 3, shade(ac, .75))
    if acc == "hat":
        R(4, 0, 11, 2, ac); R(2, 3, 13, 3, shade(ac, .85))
    if acc == "bow":
        R(3, 2, 4, 3, ac) if d != 2 else R(10, 2, 11, 3, ac); R(11, 2, 12, 3, ac) if d != 2 else None
    if acc == "beard" and not back_all:
        R(5, 6, 10, 7, ac) if d == 0 else R(4, 6, 8, 7, ac)
    # outline
    px = img.load()
    out = img.copy()
    po = out.load()
    for y in range(16):
        for x in range(16):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 16 and 0 <= ny < 16 and px[nx, ny][3] > 0:
                        po[x, y] = INK
                        break
    if mirror:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    return out


def main():
    n = len(LOOKS)
    atlas = Image.new("RGBA", (FRAMES * 16, n * 16), (0, 0, 0, 0))
    for row, look in enumerate(LOOKS):
        for d in range(4):
            for f in range(3):
                atlas.alpha_composite(draw_char(look, d, f), ((d * 3 + f) * 16, row * 16))
    assert len({atlas.crop((0, r * 16, 48, r * 16 + 16)).tobytes() for r in range(n)}) == n, "two characters look identical"
    os.makedirs(os.path.join(ROOT, "assets/characters"), exist_ok=True)
    atlas.save(os.path.join(ROOT, "assets/characters/characters.png"))
    shutil.copy(os.path.join(ROOT, "assets/characters/characters.png"), os.path.join(ROOT, "docs/assets/characters.png"))
    cast = [dict(id=l[0], name=l[1], role=l[2], row=i) for i, l in enumerate(LOOKS)]
    lines = ["class_name CharacterRoster", "extends RefCounted",
             "## GENERATED by tools/generate_characters.py. Do not edit by hand; edit LOOKS there and re-run.",
             "## characters.png: one row per character, 12 frames of 16x16 in this order:",
             "## down, up, left, right (Facing.Dir order), each as idle, walk A, walk B.", "",
             'const ATLAS_PATH := "res://assets/characters/characters.png"', "const FRAMES_PER_ROW := 12", "const CELL := 16", "", "const CAST := ["]
    lines += ["\t" + json.dumps(c, separators=(", ", ": ")) + "," for c in cast]
    lines += ["]", "", "static var _rows: Dictionary = {}", "", "",
              "static func row_of(character_id: String) -> int:", "\tif _rows.is_empty():", "\t\tfor c in CAST:", "\t\t\t_rows[c.id] = c.row",
              "\treturn _rows.get(character_id, 0)", "", "",
              "## First frame (facing down, idle) as a 16x16 texture.", "static func portrait(character_id: String) -> AtlasTexture:",
              "\tvar t := AtlasTexture.new()", "\tt.atlas = load(ATLAS_PATH)", "\tt.region = Rect2(0, row_of(character_id) * CELL, CELL, CELL)", "\treturn t", "", "", "static func display_name(character_id: String) -> String:",
              "\tfor c in CAST:", "\t\tif c.id == character_id:", "\t\t\treturn c.name", "\treturn character_id", ""]
    with open(os.path.join(ROOT, "scripts/data/character_roster.gd"), "w") as f:
        f.write("\n".join(lines))
    cols = 8
    rows = (n + cols - 1) // cols
    prev = Image.new("RGBA", (cols * 16 * 4 * 2, rows * 16 * 4), (34, 31, 56, 255))
    for i in range(n):
        for k, fr in enumerate((0, 3)):  # down idle and up idle
            tile = atlas.crop((fr * 16, i * 16, fr * 16 + 16, i * 16 + 16)).resize((64, 64), Image.NEAREST)
            prev.alpha_composite(tile, (((i % cols) * 2 + k) * 64, (i // cols) * 64))
    prev.convert("RGB").save(os.path.join(ROOT, "docs/characters_preview.png"), optimize=True)
    print("characters:", n)


if __name__ == "__main__":
    main()
