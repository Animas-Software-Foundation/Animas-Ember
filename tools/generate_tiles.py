#!/usr/bin/env python3
"""Generates the placeholder tileset for Pixel Pulse RPG.

Outputs (relative to the project root):
  assets/tilesets/tiles.png    8x4 sheet of 16x16 tiles
  assets/tilesets/tiles.tres   Godot TileSet (collision on solid tiles, "tall_grass" custom data)
  docs/tiles_preview.png       4x upscaled preview

Usage:  pip install pillow && python3 tools/generate_tiles.py

Want your own art? Either paint over tiles.png in any pixel editor (keep the
8-column, 16x16 grid) and skip this script, or edit the draw functions below.
Collision / tall-grass flags live in the TILES table.
"""
import os
import random
from PIL import Image, ImageDraw

T = 16
COLS, ROWS = 8, 4
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# ---- palette (all original colors) -----------------------------------------
GRASS, GRASS_D, GRASS_L = (104, 176, 72), (84, 152, 56), (132, 204, 92)
PATH, PATH_D = (216, 184, 128), (190, 156, 100)
SAND, SAND_D = (236, 220, 160), (214, 192, 132)
WATER, WATER_L, WATER_D = (72, 128, 216), (128, 184, 244), (56, 100, 180)
TREE_D, TREE, TREE_L, TRUNK = (28, 84, 44), (46, 124, 62), (76, 164, 84), (108, 70, 38)
WOOD, WOOD_D, WOOD_L = (176, 120, 64), (120, 76, 40), (208, 156, 96)
STONE, STONE_D, STONE_L = (140, 140, 150), (104, 104, 116), (170, 170, 180)
WALL, WALL_D = (240, 228, 200), (216, 202, 170)
ROOF_R, ROOF_R_D = (200, 72, 64), (150, 48, 48)
ROOF_B, ROOF_B_D = (64, 108, 196), (44, 76, 148)
GLASS, GLASS_L = (150, 200, 236), (210, 236, 250)
CARPET, CARPET_D = (196, 60, 72), (148, 40, 54)
OUTLINE = (40, 36, 44)


def dots(d, rng, color, n, box=(0, 0, T - 1, T - 1)):
    for _ in range(n):
        d.point((rng.randint(box[0], box[2]), rng.randint(box[1], box[3])), fill=color)


# ---- tile drawers: each receives an ImageDraw for one 16x16 tile -----------
def grass(d, seed=1):
    rng = random.Random(seed)
    d.rectangle((0, 0, 15, 15), fill=GRASS)
    dots(d, rng, GRASS_D, 10)
    dots(d, rng, GRASS_L, 6)


def grass_tufts(d):
    grass(d, seed=7)
    for x, y in [(3, 4), (11, 3), (7, 11), (13, 12)]:
        d.point((x, y), fill=GRASS_D)
        d.point((x, y - 1), fill=GRASS_D)
        d.point((x + 1, y), fill=GRASS_L)


def flowers(d):
    grass(d, seed=3)
    for (x, y), c in [((3, 3), (240, 80, 96)), ((10, 5), (250, 250, 240)), ((6, 11), (250, 210, 70)), ((13, 12), (240, 80, 96))]:
        d.point((x, y), fill=c)
        d.point((x - 1, y), fill=c)
        d.point((x + 1, y), fill=c)
        d.point((x, y - 1), fill=c)
        d.point((x, y + 1), fill=c)
        d.point((x, y), fill=(250, 230, 120))


def tall_grass(d):
    d.rectangle((0, 0, 15, 15), fill=GRASS_D)
    for bx in (1, 4, 7, 10, 13):
        for by, h in ((2 if bx % 2 else 5, 6), (9, 6)):
            d.line((bx, by + h, bx, by), fill=TREE)
            d.line((bx + 1, by + h, bx + 1, by + 2), fill=GRASS_L)
            d.point((bx, by), fill=GRASS_L)
    d.line((0, 15, 15, 15), fill=TREE_D)


def path(d):
    rng = random.Random(11)
    d.rectangle((0, 0, 15, 15), fill=PATH)
    dots(d, rng, PATH_D, 14)
    dots(d, rng, (232, 204, 152), 5)


def sand(d):
    rng = random.Random(13)
    d.rectangle((0, 0, 15, 15), fill=SAND)
    dots(d, rng, SAND_D, 12)


def water(d):
    d.rectangle((0, 0, 15, 15), fill=WATER)
    for y, x0 in ((3, 2), (9, 8), (14, 3)):
        d.line((x0, y, x0 + 4, y), fill=WATER_L)
        d.line((x0 - 2, y + 1, x0 + 1, y + 1), fill=WATER_D)


def tree(d):
    grass(d, seed=5)
    d.rectangle((6, 10, 9, 15), fill=TRUNK)
    d.line((6, 10, 6, 15), fill=WOOD_D)
    d.ellipse((1, 0, 14, 12), fill=TREE, outline=TREE_D)
    d.ellipse((4, 2, 8, 5), fill=TREE_L)
    d.point((10, 6), fill=TREE_D)
    d.point((6, 8), fill=TREE_D)


def bush(d):
    grass(d, seed=9)
    d.ellipse((1, 5, 14, 14), fill=TREE, outline=TREE_D)
    d.ellipse((3, 6, 7, 9), fill=TREE_L)
    d.point((10, 10), fill=(240, 80, 96))
    d.point((7, 12), fill=(240, 80, 96))


def fence(d):
    grass(d, seed=15)
    for x0 in (1, 11):
        d.rectangle((x0, 4, x0 + 2, 14), fill=WOOD, outline=WOOD_D)
    for y in (6, 10):
        d.rectangle((0, y, 15, y + 2), fill=WOOD_L, outline=WOOD_D)


def sign(d):
    grass(d, seed=17)
    d.rectangle((7, 8, 8, 14), fill=WOOD_D)
    d.rectangle((2, 1, 13, 8), fill=WOOD_L, outline=WOOD_D)
    d.line((4, 4, 11, 4), fill=WOOD_D)
    d.line((4, 6, 9, 6), fill=WOOD_D)


def stone_wall(d):
    d.rectangle((0, 0, 15, 15), fill=STONE)
    for y in (0, 5, 10):
        d.line((0, y, 15, y), fill=STONE_D)
    for y, xs in ((0, (4, 12)), (5, (0, 8)), (10, (4, 12))):
        for x in xs:
            d.line((x, y, x, y + 4), fill=STONE_D)
    d.line((0, 15, 15, 15), fill=STONE_D)
    for x, y in ((1, 1), (9, 6), (5, 11)):
        d.point((x, y), fill=STONE_L)


def wood_floor(d):
    d.rectangle((0, 0, 15, 15), fill=WOOD_L)
    for y in (3, 7, 11, 15):
        d.line((0, y, 15, y), fill=WOOD)
    for x, y in ((4, 0), (11, 4), (6, 8), (13, 12)):
        d.line((x, y, x, y + 3), fill=WOOD)


def carpet(d):
    d.rectangle((0, 0, 15, 15), fill=CARPET)
    d.rectangle((0, 0, 15, 15), outline=CARPET_D)
    d.rectangle((3, 3, 12, 12), outline=(236, 196, 90))
    d.point((7, 7), fill=(236, 196, 90))
    d.point((8, 8), fill=(236, 196, 90))


def roof(d, main, dark):
    d.rectangle((0, 0, 15, 15), fill=main)
    for y in (0, 4, 8, 12):
        d.line((0, y + 3, 15, y + 3), fill=dark)
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(off, 16, 8):
            d.line((x, y, x, y + 2), fill=dark)


def roof_red(d):
    roof(d, ROOF_R, ROOF_R_D)


def roof_blue(d):
    roof(d, ROOF_B, ROOF_B_D)


def house_wall(d):
    d.rectangle((0, 0, 15, 15), fill=WALL)
    for y in (4, 9, 14):
        d.line((0, y, 15, y), fill=WALL_D)
    d.line((0, 15, 15, 15), fill=(190, 176, 146))


def window_wall(d):
    house_wall(d)
    d.rectangle((3, 3, 12, 11), fill=GLASS, outline=WOOD_D)
    d.line((7, 3, 7, 11), fill=WOOD_D)
    d.line((8, 3, 8, 11), fill=WOOD_D)
    d.line((3, 7, 12, 7), fill=WOOD_D)
    d.point((4, 4), fill=GLASS_L)
    d.point((9, 4), fill=GLASS_L)


def door(d):
    house_wall(d)
    d.rectangle((3, 1, 12, 15), fill=WOOD, outline=WOOD_D)
    d.rectangle((5, 3, 10, 7), outline=WOOD_D)
    d.rectangle((5, 9, 10, 13), outline=WOOD_D)
    d.point((10, 8), fill=(250, 220, 90))


def door_mat(d):
    wood_floor(d)
    d.rectangle((2, 4, 13, 11), fill=(86, 100, 150), outline=(54, 64, 110))
    d.line((4, 7, 11, 7), fill=(130, 146, 200))


def counter(d):
    d.rectangle((0, 0, 15, 15), fill=WOOD_L)
    d.rectangle((0, 0, 15, 5), fill=(224, 176, 116), outline=WOOD_D)
    d.rectangle((0, 6, 15, 15), fill=WOOD, outline=WOOD_D)
    d.line((7, 8, 8, 8), fill=(250, 220, 90))


def bookshelf(d):
    d.rectangle((0, 0, 15, 15), fill=WOOD, outline=WOOD_D)
    colors = [(200, 64, 72), (64, 108, 196), (80, 168, 96), (236, 196, 90), (150, 90, 190)]
    for row, y in enumerate((2, 9)):
        d.line((1, y + 5, 14, y + 5), fill=WOOD_D)
        x = 2
        for i in range(5):
            w = 2 + (i + row) % 2
            d.rectangle((x, y, x + w - 1, y + 4), fill=colors[(i + row * 2) % 5])
            x += w + 1


def ledge(d):
    grass(d, seed=21)
    d.rectangle((0, 10, 15, 11), fill=GRASS_D)
    d.rectangle((0, 12, 15, 15), fill=(120, 96, 64))
    d.line((0, 12, 15, 12), fill=(90, 70, 44))
    for x in (2, 7, 12):
        d.point((x, 14), fill=(150, 124, 86))


# ---- tile table: (col, row, name, draw_fn, solid, tall_grass) ---------------
TILES = [
    (0, 0, "grass",        grass,        False, False),
    (1, 0, "grass_tufts",  grass_tufts,  False, False),
    (2, 0, "flowers",      flowers,      False, False),
    (3, 0, "tall_grass",   tall_grass,   False, True),
    (4, 0, "path",         path,         False, False),
    (5, 0, "sand",         sand,         False, False),
    (6, 0, "water",        water,        True,  False),
    (0, 1, "tree",         tree,         True,  False),
    (1, 1, "bush",         bush,         True,  False),
    (2, 1, "fence",        fence,        True,  False),
    (3, 1, "sign",         sign,         True,  False),
    (4, 1, "stone_wall",   stone_wall,   True,  False),
    (5, 1, "wood_floor",   wood_floor,   False, False),
    (6, 1, "carpet",       carpet,       False, False),
    (7, 1, "roof_red",     roof_red,     True,  False),
    (0, 2, "roof_blue",    roof_blue,    True,  False),
    (1, 2, "house_wall",   house_wall,   True,  False),
    (2, 2, "window_wall",  window_wall,  True,  False),
    (3, 2, "door",         door,         False, False),
    (4, 2, "door_mat",     door_mat,     False, False),
    (5, 2, "counter",      counter,      True,  False),
    (6, 2, "bookshelf",    bookshelf,    True,  False),
    (7, 2, "ledge",        ledge,        True,  False),
]


def build_png():
    sheet = Image.new("RGBA", (COLS * T, ROWS * T), (0, 0, 0, 0))
    for col, row, _name, fn, _solid, _tg in TILES:
        tile = Image.new("RGBA", (T, T), (0, 0, 0, 0))
        fn(ImageDraw.Draw(tile))
        sheet.paste(tile, (col * T, row * T))
    out = os.path.join(ROOT, "assets", "tilesets", "tiles.png")
    sheet.save(out)
    prev = sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST)
    prev.save(os.path.join(ROOT, "docs", "tiles_preview.png"))
    return out


def build_tres():
    box = "PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)"
    lines = [
        '[gd_resource type="TileSet" load_steps=3 format=3]',
        "",
        '[ext_resource type="Texture2D" path="res://assets/tilesets/tiles.png" id="1_tiles"]',
        "",
        '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_tiles"]',
        'texture = ExtResource("1_tiles")',
        "texture_region_size = Vector2i(16, 16)",
    ]
    for col, row, _name, _fn, solid, tall in sorted(TILES, key=lambda t: (t[0], t[1])):
        lines.append(f"{col}:{row}/0 = 0")
        if solid:
            lines.append(f"{col}:{row}/0/physics_layer_0/polygon_0/points = {box}")
        if tall:
            lines.append(f"{col}:{row}/0/custom_data_0 = true")
    lines += [
        "",
        "[resource]",
        "tile_size = Vector2i(16, 16)",
        "physics_layer_0/collision_layer = 1",
        'custom_data_layer_0/name = "tall_grass"',
        "custom_data_layer_0/type = 1",
        'sources/0 = SubResource("TileSetAtlasSource_tiles")',
        "",
    ]
    out = os.path.join(ROOT, "assets", "tilesets", "tiles.tres")
    with open(out, "w") as f:
        f.write("\n".join(lines))
    return out


if __name__ == "__main__":
    print("wrote", build_png())
    print("wrote", build_tres())
