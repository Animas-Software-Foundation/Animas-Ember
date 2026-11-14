#!/usr/bin/env python3
"""Generates "Animas Pixel", the game's bitmap font, from hand-drawn glyph bitmaps.

Outputs (relative to the project root):
  assets/fonts/animas_pixel.png   glyph atlas (white pixels on transparent)
  assets/fonts/animas_pixel.fnt   BMFont text descriptor (Godot imports this natively)
  docs/font_preview.png           4x upscaled specimen

Usage:  pip install pillow && python3 tools/generate_font.py

Design: 5 px wide, 7 px cap height, 5 px x-height, 2 px descenders, proportional
spacing. Every glyph is drawn below as rows of "#" (ink) and "." (empty). The
format of each entry is  char: (top_row, "row|row|...")  where top_row is the
vertical position inside the 9 px cell (0 = cap line, 2 = x-height line,
7 = first descender row, baseline sits below row 6).

Use the font at its native size (9) so it stays perfectly crisp.
"""
import os
from PIL import Image, ImageDraw

CELL_H, BASE, LINE_H, SIZE = 9, 7, 10, 9
SPACE_ADVANCE = 3
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

G = {
    # --- capitals (7 rows) ---
    "A": (0, ".###.|#...#|#...#|#####|#...#|#...#|#...#"),
    "B": (0, "####.|#...#|#...#|####.|#...#|#...#|####."),
    "C": (0, ".####|#....|#....|#....|#....|#....|.####"),
    "D": (0, "####.|#...#|#...#|#...#|#...#|#...#|####."),
    "E": (0, "#####|#....|#....|####.|#....|#....|#####"),
    "F": (0, "#####|#....|#....|####.|#....|#....|#...."),
    "G": (0, ".####|#....|#....|#.###|#...#|#...#|.###."),
    "H": (0, "#...#|#...#|#...#|#####|#...#|#...#|#...#"),
    "I": (0, "###|.#.|.#.|.#.|.#.|.#.|###"),
    "J": (0, "..###|...#.|...#.|...#.|...#.|#..#.|.##.."),
    "K": (0, "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#"),
    "L": (0, "#....|#....|#....|#....|#....|#....|#####"),
    "M": (0, "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#"),
    "N": (0, "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#"),
    "O": (0, ".###.|#...#|#...#|#...#|#...#|#...#|.###."),
    "P": (0, "####.|#...#|#...#|####.|#....|#....|#...."),
    "Q": (0, ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#"),
    "R": (0, "####.|#...#|#...#|####.|#.#..|#..#.|#...#"),
    "S": (0, ".####|#....|#....|.###.|....#|....#|####."),
    "T": (0, "#####|..#..|..#..|..#..|..#..|..#..|..#.."),
    "U": (0, "#...#|#...#|#...#|#...#|#...#|#...#|.###."),
    "V": (0, "#...#|#...#|#...#|#...#|#...#|.#.#.|..#.."),
    "W": (0, "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#"),
    "X": (0, "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#"),
    "Y": (0, "#...#|#...#|.#.#.|..#..|..#..|..#..|..#.."),
    "Z": (0, "#####|....#|...#.|..#..|.#...|#....|#####"),
    # --- lowercase ---
    "a": (2, ".###.|....#|.####|#...#|.####"),
    "b": (0, "#....|#....|####.|#...#|#...#|#...#|####."),
    "c": (2, ".###.|#...#|#....|#...#|.###."),
    "d": (0, "....#|....#|.####|#...#|#...#|#...#|.####"),
    "e": (2, ".###.|#...#|#####|#....|.###."),
    "f": (0, "..##.|.#..#|.#...|###..|.#...|.#...|.#..."),
    "g": (2, ".####|#...#|#...#|#...#|.####|....#|.###."),
    "h": (0, "#....|#....|####.|#...#|#...#|#...#|#...#"),
    "i": (0, "#|.|#|#|#|#|#"),
    "j": (0, "..#|...|..#|..#|..#|..#|..#|#.#|.#."),
    "k": (0, "#....|#....|#..#.|#.#..|##...|#.#..|#..#."),
    "l": (0, "##.|.#.|.#.|.#.|.#.|.#.|.##"),
    "m": (2, "##.#.|#.#.#|#.#.#|#.#.#|#...#"),
    "n": (2, "####.|#...#|#...#|#...#|#...#"),
    "o": (2, ".###.|#...#|#...#|#...#|.###."),
    "p": (2, "####.|#...#|#...#|#...#|####.|#....|#...."),
    "q": (2, ".####|#...#|#...#|#...#|.####|....#|....#"),
    "r": (2, "#.##.|##..#|#....|#....|#...."),
    "s": (2, ".####|#....|.###.|....#|####."),
    "t": (1, ".#..|###.|.#..|.#..|.#.#|..#."),
    "u": (2, "#...#|#...#|#...#|#..##|.##.#"),
    "v": (2, "#...#|#...#|#...#|.#.#.|..#.."),
    "w": (2, "#...#|#...#|#.#.#|#.#.#|.#.#."),
    "x": (2, "#...#|.#.#.|..#..|.#.#.|#...#"),
    "y": (2, "#...#|#...#|#...#|.####|....#|#...#|.###."),
    "z": (2, "#####|...#.|..#..|.#...|#####"),
    # --- digits ---
    "0": (0, ".###.|#...#|#..##|#.#.#|##..#|#...#|.###."),
    "1": (0, ".#.|##.|.#.|.#.|.#.|.#.|###"),
    "2": (0, ".###.|#...#|....#|...#.|..#..|.#...|#####"),
    "3": (0, "####.|....#|....#|.###.|....#|....#|####."),
    "4": (0, "...#.|..##.|.#.#.|#..#.|#####|...#.|...#."),
    "5": (0, "#####|#....|####.|....#|....#|#...#|.###."),
    "6": (0, ".###.|#....|#....|####.|#...#|#...#|.###."),
    "7": (0, "#####|....#|...#.|..#..|..#..|..#..|..#.."),
    "8": (0, ".###.|#...#|#...#|.###.|#...#|#...#|.###."),
    "9": (0, ".###.|#...#|#...#|.####|....#|....#|.###."),
    # --- punctuation & symbols ---
    "!": (0, "#|#|#|#|#|.|#"),
    '"': (0, "#.#|#.#"),
    "#": (0, ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#."),
    "$": (0, "..#..|.####|#.#..|.###.|..#.#|####.|..#.."),
    "%": (0, "##..#|##..#|...#.|..#..|.#...|#..##|#..##"),
    "&": (0, ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#"),
    "'": (0, "#|#"),
    "(": (0, "..#|.#.|#..|#..|#..|.#.|..#"),
    ")": (0, "#..|.#.|..#|..#|..#|.#.|#.."),
    "*": (1, "..#..|#.#.#|.###.|#.#.#|..#.."),
    "+": (2, "..#..|..#..|#####|..#..|..#.."),
    ",": (6, "#|#"),
    "-": (4, "####."),
    ".": (6, "#"),
    "/": (0, "....#|....#|...#.|..#..|.#...|#....|#...."),
    ":": (3, "#|.|#"),
    ";": (3, "#|.|#|#"),
    "<": (2, "..#|.#.|#..|.#.|..#"),
    "=": (3, "#####|.....|#####"),
    ">": (2, "#..|.#.|..#|.#.|#.."),
    "?": (0, ".###.|#...#|....#|...#.|..#..|.....|..#.."),
    "@": (0, ".###.|#...#|#.###|#.#.#|#.###|#....|.###."),
    "[": (0, "###|#..|#..|#..|#..|#..|###"),
    "\\": (0, "#....|#....|.#...|..#..|...#.|....#|....#"),
    "]": (0, "###|..#|..#|..#|..#|..#|###"),
    "^": (0, ".#.|#.#"),
    "_": (8, "#####"),
    "`": (0, "#.|.#"),
    "{": (0, "..##|.#..|.#..|#...|.#..|.#..|..##"),
    "|": (0, "#|#|#|#|#|#|#|#|#"),
    "}": (0, "##..|..#.|..#.|...#|..#.|..#.|##.."),
    "~": (3, ".##.#|#.##."),
}


def glyph_bitmap(top, rows):
    """-> (set of (x, y) ink pixels, ink width)."""
    px = set()
    for dy, row in enumerate(rows.split("|")):
        for x, ch in enumerate(row):
            if ch == "#":
                px.add((x, top + dy))
    width = max(x for x, _ in px) + 1
    return px, width


def build():
    codes = list(range(32, 127))
    cols, pad = 16, 1
    cw, ch = 5 + 2 * pad + 1, CELL_H + 2 * pad
    rows_n = (len(codes) + cols - 1) // cols
    atlas = Image.new("RGBA", (cols * cw, rows_n * ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(atlas)
    lines = []
    for i, code in enumerate(codes):
        c = chr(code)
        ox, oy = (i % cols) * cw + pad, (i // cols) * ch + pad
        if c == " ":
            lines.append((code, ox, oy, 0, 0, SPACE_ADVANCE))
            continue
        px, width = glyph_bitmap(*G[c])
        for x, y in px:
            d.point((ox + x, oy + y), fill=(255, 255, 255, 255))
        lines.append((code, ox, oy, width, CELL_H, width + 1))
    missing = [chr(c) for c in codes if chr(c) != " " and chr(c) not in G]
    assert not missing, "missing glyphs: %r" % missing

    fonts = os.path.join(ROOT, "assets", "fonts")
    os.makedirs(fonts, exist_ok=True)
    atlas.save(os.path.join(fonts, "animas_pixel.png"))
    out = [
        'info face="Animas Pixel" size=%d bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=0 padding=0,0,0,0 spacing=0,0 outline=0' % SIZE,
        "common lineHeight=%d base=%d scaleW=%d scaleH=%d pages=1 packed=0 alphaChnl=0 redChnl=4 greenChnl=4 blueChnl=4"
        % (LINE_H, BASE, atlas.width, atlas.height),
        'page id=0 file="animas_pixel.png"',
        "chars count=%d" % len(lines),
    ]
    for code, x, y, w, h, adv in lines:
        out.append("char id=%d x=%d y=%d width=%d height=%d xoffset=0 yoffset=0 xadvance=%d page=0 chnl=15" % (code, x, y, w, h, adv))
    with open(os.path.join(fonts, "animas_pixel.fnt"), "w") as f:
        f.write("\n".join(out) + "\n")
    return atlas, dict((c, (x, y, w, h, a)) for c, x, y, w, h, a in lines)


def specimen(atlas, metrics):
    texts = ["ANIMAS: EMBER", "The quick brown fox jumps over the lazy dog.",
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
             "0123456789 !?.,:;'\"()[]{}<>+-=*/\\|_~#$%&@^`"]
    img = Image.new("RGBA", (300, 12 * len(texts) + 6), (32, 34, 44, 255))
    y = 4
    for t in texts:
        x = 4
        for ch in t:
            gx, gy, w, h, adv = metrics[ord(ch)]
            if w:
                img.alpha_composite(atlas.crop((gx, gy, gx + w, gy + h)), (x, y))
            x += adv
        y += 12
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(os.path.join(ROOT, "docs", "font_preview.png"))


if __name__ == "__main__":
    a, m = build()
    specimen(a, m)
    print("wrote assets/fonts/animas_pixel.{png,fnt} and docs/font_preview.png")
