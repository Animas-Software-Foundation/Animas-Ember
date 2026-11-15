#!/usr/bin/env python3
"""Generates all 151 animas: sprites, stats, evolution chains, and dex text.

Outputs (relative to the project root):
  assets/animas/animas.png      512x320 atlas, 16 columns of 32x32 sprites (id N is cell N-1)
  scripts/data/anima_roster.gd  the roster as GDScript data (do not edit by hand)
  docs/assets/animas.png        copy of the atlas for the website
  docs/animas_preview.png       2x preview of the whole roster

Usage:  pip install pillow && python3 tools/generate_animas.py
To add or change an anima, edit FAMILIES below and re-run. Everything is deterministic.
"""
import json
import os
import random
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anima_art as art  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TYPES = ["Ember", "Tide", "Bloom", "Volt", "Stone", "Gale", "Frost", "Shade", "Lumen", "Venom", "Iron", "Wild"]

# (stage names, types, body archetype, features in the order they are gained, dex blurb)
FAMILIES = [
    # ---- three-stage lines (ids 1-90) ----
    (("Cindle", "Pyrelet", "Embrix"), ("Ember",), "dragon", ("tail_flame", "horn", "wings"), "Its tail flame glows brighter when it is happy and sputters when it is sad."),
    (("Brookit", "Tortide", "Marelith"), ("Tide",), "quad", ("shell", "tail_fin", "crest"), "It carries a tiny pond on its shell and sprays rain at anyone who sneaks up."),
    (("Sproutle", "Thornpup", "Verdantis"), ("Bloom",), "quad", ("tail_leaf", "ears", "mane"), "The sprout on its back drinks sunlight, so it naps in meadows to grow."),
    (("Zaplet", "Voltiger", "Thunderra"), ("Volt",), "quad", ("tail_bolt", "ears", "mane"), "Static crackles through its fur and lights up whenever it runs."),
    (("Pebblit", "Cragnoid", "Monolith"), ("Stone",), "golem", ("spikes", "crest", "horn"), "It sleeps so still that travelers mistake it for a boulder."),
    (("Puffling", "Galewing", "Tempestra"), ("Gale",), "bird", ("crest", "wings", "tail_tuft"), "It rides storm fronts and gathers wind in its feathers."),
    (("Frostkit", "Glacipaw", "Cryowolf"), ("Frost",), "quad", ("ears", "mane", "fangs"), "Its breath freezes into snowflakes that never melt in its den."),
    (("Dimlet", "Gloamer", "Umbraxis"), ("Shade",), "bat", ("ears", "fangs", "tail_tuft"), "It hangs in the dark and hums a song that makes lanterns flicker."),
    (("Glimmer", "Lumeo", "Solarion"), ("Lumen",), "orb", ("halo", "wings", "crest"), "A drifting spark of light that follows lost travelers home."),
    (("Toxling", "Venomar", "Plaguebloom"), ("Venom",), "plant", ("spikes", "tail_leaf", "crest"), "Its sweet perfume is harmless, but its thorns are not."),
    (("Rivett", "Ferrox", "Ironarch"), ("Iron",), "biped", ("horn", "spikes", "crest"), "It hammers its own plating into shape and polishes it every dawn."),
    (("Snuffle", "Burrowl", "Wildmane"), ("Wild",), "quad", ("ears", "tail_tuft", "mane"), "It digs cozy burrows and shares them with anyone who is cold."),
    (("Sparkbug", "Cindermoth", "Pyrewing"), ("Ember", "Gale"), "bug", ("wings", "flamehead", "crest"), "It dances around campfires and scatters glowing dust."),
    (("Bubblet", "Finnick", "Leviathar"), ("Tide",), "fish", ("crest", "fangs", "spikes"), "It blows bubbles that pop into tiny rainbows."),
    (("Mossling", "Fernoid", "Elderoot"), ("Bloom", "Stone"), "plant", ("tail_leaf", "crest", "horn"), "Moss grows on its back, and whole ferns grow as it ages."),
    (("Zinger", "Arcbat", "Stormflux"), ("Volt", "Gale"), "bat", ("tail_bolt", "ears", "fangs"), "It swoops through thunderclouds and recharges on lightning."),
    (("Chillet", "Snowdrift", "Blizzarch"), ("Frost", "Gale"), "bird", ("crest", "wings", "tail_tuft"), "Its wingbeats sprinkle snow over the mountain passes."),
    (("Wisp", "Phantelle", "Spectrum"), ("Shade", "Lumen"), "ghost", ("ears", "crest", "halo"), "It glows softly in old ruins, guarding memories left behind."),
    (("Sandpip", "Dunecrab", "Colossand"), ("Stone", "Tide"), "crab", ("horn", "crest", "spikes"), "It scuttles along beaches and shapes sand castles with its claws."),
    (("Hissle", "Serpine", "Basilox"), ("Venom",), "snake", ("fangs", "crest", "horn"), "It coils around warm rocks and watches everything with one eye open."),
    (("Clinkit", "Gearhound", "Mechadon"), ("Iron", "Volt"), "quad", ("spikes", "tail_bolt", "horn"), "Its clicking joints hum when it is thinking, and sing when it is excited."),
    (("Dewdrop", "Ripplet", "Oceanix"), ("Tide", "Lumen"), "blob", ("ears", "tail_fin", "halo"), "A glowing drop of seawater that grows with every tide it rides."),
    (("Magmite", "Lavaling", "Volcanox"), ("Ember", "Stone"), "golem", ("flamehead", "spikes", "horn"), "Molten rock glows in its cracks, and it warms the cave where it sleeps."),
    (("Petalet", "Blossima", "Floraqueen"), ("Bloom", "Lumen"), "plant", ("tail_leaf", "crest", "halo"), "Its petals open at dawn and fill the air with a soothing scent."),
    (("Nibbly", "Chompurr", "Mawtooth"), ("Wild", "Shade"), "quad", ("ears", "fangs", "whiskers"), "It nibbles on everything, then purrs when it finds something tasty."),
    (("Fluffin", "Cloudrake", "Stratosoar"), ("Gale", "Lumen"), "bird", ("tail_tuft", "wings", "halo"), "It sleeps on clouds and wakes the sun with its call."),
    (("Rustle", "Scrapjack", "Junkarch"), ("Iron", "Shade"), "biped", ("spikes", "horn", "crest"), "It assembles armor from scrap, no matter how odd the parts."),
    (("Gleamite", "Crystalor", "Prismarch"), ("Stone", "Lumen"), "golem", ("crest", "halo", "spikes"), "Crystals on its body split sunlight into dazzling colors."),
    (("Marshmo", "Boggle", "Swampotent"), ("Tide", "Venom"), "blob", ("tail_fin", "spikes", "fangs"), "It lurks in bogs, and its bubbling belly gives off a strange glow."),
    (("Sparklet", "Flarebird", "Phoenyx"), ("Ember", "Gale"), "bird", ("tail_flame", "flamehead", "wings"), "Legends say it returns from its own ashes at the break of dawn."),
    # ---- two-stage lines (ids 91-130) ----
    (("Nutkin", "Acornard"), ("Wild", "Bloom"), "quad", ("tail_tuft", "ears"), "It hoards acorns and forgets where it hid them, so forests grow."),
    (("Chirpa", "Songbeak"), ("Gale",), "bird", ("crest", "wings"), "Its song carries for miles and calms every anima that hears it."),
    (("Drowzel", "Dreamaw"), ("Shade", "Wild"), "quad", ("ears", "fangs"), "It naps constantly, and its dreams drift out as faint violet mist."),
    (("Tadgle", "Pondrake"), ("Tide",), "blob", ("crest", "tail_fin"), "It leaps from lily pad to lily pad and sings after the rain."),
    (("Bristlet", "Quillback"), ("Wild", "Venom"), "quad", ("spikes", "ears"), "Its quills rattle as a warning before it ever needs to use them."),
    (("Fidget", "Zipwing"), ("Volt",), "bug", ("wings", "tail_bolt"), "It zips around so fast that it leaves faint trails of sparks."),
    (("Cobble", "Boulderback"), ("Stone",), "quad", ("shell", "horn"), "It tucks into its stony shell and rolls downhill for fun."),
    (("Icicle", "Frozerk"), ("Frost",), "biped", ("crest", "horn"), "It builds snow forts and defends them with surprising fury."),
    (("Wickle", "Candelume"), ("Lumen", "Ember"), "ghost", ("flamehead", "halo"), "A gentle flame that lights the way through haunted halls."),
    (("Marble", "Orbitron"), ("Iron",), "orb", ("spikes", "halo"), "A perfectly round metal anima that hovers in slow orbits."),
    (("Mudder", "Quagmire"), ("Stone", "Tide"), "blob", ("spikes", "fangs"), "It loves puddles and splashes everyone who walks by."),
    (("Thistle", "Burrdor"), ("Bloom", "Venom"), "plant", ("spikes", "crest"), "It clings to passers-by and rides along to new places."),
    (("Scuttle", "Pincerlord"), ("Tide", "Iron"), "crab", ("horn", "spikes"), "Its steel-hard claws can crack a coconut in one snap."),
    (("Hopper", "Springald"), ("Wild", "Gale"), "quad", ("longears", "tail_tuft"), "Its powerful legs let it bound across whole valleys."),
    (("Smolder", "Blazewyrm"), ("Ember",), "snake", ("flamehead", "fangs"), "It slithers through volcano vents and leaves scorched trails."),
    (("Gloomlet", "Eclipsor"), ("Shade", "Lumen"), "orb", ("halo", "wings"), "It floats between light and dark, and eclipses the moon when it glides."),
    (("Mogger", "Voltmole"), ("Volt", "Stone"), "quad", ("ears", "tail_bolt"), "It tunnels underground and shocks the soil to loosen it."),
    (("Glowfin", "Anglurk"), ("Tide", "Lumen"), "fish", ("halo", "fangs"), "A lantern on its head lures curious animas out of deep waters."),
    (("Spinnet", "Arachnix"), ("Venom",), "bug", ("spikes", "fangs"), "It weaves silk threads that shimmer like moonlit dew."),
    (("Fawnle", "Stagheart"), ("Wild", "Bloom"), "quad", ("horn", "tail_leaf"), "Flowers sprout from its antlers whenever it feels at peace."),
    # ---- single-stage animas (ids 131-151) ----
    (("Gigalith",), ("Stone",), "golem", ("spikes", "horn", "crest"), "A walking mountain that has not moved in a hundred years."),
    (("Aurorix",), ("Frost", "Lumen"), "dragon", ("wings", "halo", "horn"), "The shimmer of its wings paints auroras across the winter sky."),
    (("Draconyx",), ("Wild", "Ember"), "dragon", ("wings", "horn", "tail_flame"), "It circles mountain peaks and guards ancient treasure."),
    (("Ghoulantern",), ("Shade", "Ember"), "ghost", ("flamehead", "fangs"), "Its cold blue flame leads wanderers in circles all night."),
    (("Thunderoc",), ("Volt", "Gale"), "bird", ("wings", "tail_bolt", "crest"), "It crosses the sky in a flash, and thunder always trails behind."),
    (("Krakenjaw",), ("Tide", "Shade"), "fish", ("fangs", "spikes", "crest"), "It lurks in the deepest trenches, where no light reaches."),
    (("Bladeroach",), ("Iron", "Bloom"), "bug", ("horn", "spikes", "wings"), "Its razor-sharp wings can slice through bamboo in a single sweep."),
    (("Whirlimp",), ("Gale",), "orb", ("ears", "wings", "tail_tuft"), "A mischievous gust that tangles hair and steals hats."),
    (("Seraphyx",), ("Lumen",), "bird", ("wings", "halo", "crest"), "It descends only to bless those who show kindness to others."),
    (("Obsidrake",), ("Stone", "Shade"), "dragon", ("spikes", "horn", "wings"), "Born in a volcano, its scales are as sharp as black glass."),
    (("Venomaw",), ("Venom", "Shade"), "snake", ("fangs", "horn", "crest"), "A single drop of its venom is said to put a whole village to sleep."),
    (("Eldertree",), ("Bloom",), "plant", ("crest", "tail_leaf", "horn"), "Birds nest in its branches, and it remembers every season."),
    (("Mirage",), ("Lumen", "Shade"), "orb", ("halo", "wings", "fangs"), "It appears in the desert heat, and no one is sure it is real."),
    (("Ironclad",), ("Iron",), "golem", ("horn", "spikes", "crest"), "Forged long ago, it still stands guard over a forgotten gate."),
    (("Stormcrow",), ("Volt", "Shade"), "bat", ("tail_bolt", "fangs", "ears"), "It flies in the middle of the thunderstorm, laughing."),
    (("Magmaw",), ("Ember",), "blob", ("flamehead", "fangs", "spikes"), "A bubbling mass of magma that warms itself on cold nights."),
    (("Pixiebloom",), ("Bloom", "Lumen"), "orb", ("halo", "wings", "tail_leaf"), "Flowers bloom wherever its glittering dust falls."),
    (("Hoarfrost",), ("Frost",), "biped", ("crest", "horn", "mane"), "It roams blizzards, and travelers say it is gentle with the lost."),
    (("Scorchhound",), ("Ember", "Wild"), "quad", ("mane", "tail_flame", "fangs"), "It runs beside campfire smoke and guards its pack with fierce loyalty."),
    (("Tidecaller",), ("Tide", "Lumen"), "snake", ("halo", "crest", "fangs"), "Its song calls the tides, and fishers follow it home."),
    (("Animus",), ("Wild",), "orb", ("halo", "wings", "mane"), "The first anima. Its ember is said to light every other anima's spark."),
]
assert len(FAMILIES) == 71
STAGE_TEXT = {1: "It is still young and curious about everything.", 2: "It has grown bolder and fights to protect its friends.",
              3: "Fully grown, it is proud, strong, and fiercely loyal.", 0: "It is rarely seen and prefers to keep to itself."}
ROLES = {"golem": "tank", "crab": "tank", "blob": "tank", "plant": "tank", "bird": "spd", "bat": "spd", "bug": "spd", "fish": "spd",
         "dragon": "atk", "snake": "atk", "ghost": "atk", "quad": "bal", "biped": "bal", "orb": "bal"}
WEIGHTS = {"tank": [.25, .17, .28, .10, .20], "spd": [.15, .22, .13, .30, .20], "atk": [.17, .28, .14, .18, .23], "bal": [.2] * 5}
HEIGHT = {"golem": 1.6, "dragon": 1.5, "crab": .7, "blob": .6, "plant": .8, "bird": .8, "bat": .7, "bug": .6, "fish": .9, "snake": 1.8, "ghost": 1.0, "quad": .8, "biped": 1.1, "orb": .6}
PATTERNS = [None, "belly", "belly", "stripes", "spots", "belly+spots"]
EYES = ["dot", "dot", "round", "round", "angry", "sleepy", "big", "big"]


def build():
    animas, sprites, uid = [], [], 0
    for fi, (names, types, arch, feats, blurb) in enumerate(FAMILIES):
        n = len(names)
        frng = random.Random(fi * 7919 + 13)
        spec = dict(types=types, arch=arch, pattern=frng.choice(PATTERNS), eye=frng.choice(EYES))
        scales = {3: [0.62, 0.8, 1.0], 2: [0.7, 1.0], 1: [0.95]}[n]
        totals = {3: [310, 425, 540], 2: [330, 480]}.get(n) or [frng.randint(470, 590)]
        role = ROLES[arch]
        if fi == 70:
            totals = [600]
        for si, name in enumerate(names):
            uid += 1
            feats_here = feats[: si + 1] if n > 1 else feats
            if n == 2 and si == 1:
                feats_here = feats
            img = art.render(spec, feats_here, scales[si], fi * 100)
            sprites.append(img)
            r = random.Random(uid * 31 + 5)
            w = [x * r.uniform(0.88, 1.12) for x in WEIGHTS[role]]
            tot = totals[si]
            stats = [max(15, round(tot * x / sum(w))) for x in w]
            stage = si + 1 if n > 1 else 0
            animas.append(dict(
                id=uid, name=name, family=fi, stage=si + 1, stages=n, types=list(types), stats=stats,
                evolves_to=uid + 1 if si < n - 1 else 0, evolve_level=(16 + si * 16 + r.randint(0, 3)) if n == 3 else (28 + r.randint(0, 6) if n == 2 and si == 0 else 0),
                height=round(HEIGHT[arch] * (0.55 + 0.45 * (si + 1) / n) * r.uniform(0.9, 1.1), 1),
                weight=round(HEIGHT[arch] * 14 * (0.5 + si) * r.uniform(0.8, 1.3), 1),
                catch_rate=[255, 120, 45][si] if n == 3 else ([190, 60][si] if n == 2 else 25),
                dex=blurb + " " + STAGE_TEXT[stage]))
    return animas, sprites


def main():
    animas, sprites = build()
    assert len(animas) == 151, len(animas)
    names = [a["name"] for a in animas]
    assert len(set(names)) == 151, "duplicate names"
    hashes = {s.tobytes() for s in sprites}
    assert len(hashes) == 151, "identical sprites: %d unique" % len(hashes)
    cols, rows = 16, 10
    atlas = Image.new("RGBA", (cols * 32, rows * 32), (0, 0, 0, 0))
    for i, s in enumerate(sprites):
        atlas.alpha_composite(s, ((i % cols) * 32, (i // cols) * 32))
    os.makedirs(os.path.join(ROOT, "assets/animas"), exist_ok=True)
    atlas.save(os.path.join(ROOT, "assets/animas/animas.png"))
    shutil.copy(os.path.join(ROOT, "assets/animas/animas.png"), os.path.join(ROOT, "docs/assets/animas.png"))
    prev = Image.new("RGBA", (cols * 64, rows * 64), (34, 31, 56, 255))
    prev.alpha_composite(atlas.resize((atlas.width * 2, atlas.height * 2), Image.NEAREST))
    prev.convert("RGB").save(os.path.join(ROOT, "docs/animas_preview.png"), optimize=True)

    lines = ["class_name AnimaRoster", "extends RefCounted",
             "## GENERATED by tools/generate_animas.py. Do not edit by hand; edit FAMILIES there and re-run.",
             "## Stats are [hp, attack, defense, speed, special].", "",
             "const COUNT := %d" % len(animas), "const TYPES := %s" % json.dumps(TYPES),
             'const ATLAS_PATH := "res://assets/animas/animas.png"', "const ATLAS_COLUMNS := 16", "const CELL := 32", "", "const ANIMAS := ["]
    for a in animas:
        lines.append("\t" + json.dumps(a, separators=(", ", ": ")) + ",")
    lines += ["]", "",
              "static var _by_name: Dictionary = {}", "static var _icons: Dictionary = {}", "",
              "", "static func get_anima(id: int) -> Dictionary:", "\treturn ANIMAS[clampi(id, 1, COUNT) - 1]", "", "",
              "static func id_of(anima_name: String) -> int:", "\tif _by_name.is_empty():",
              "\t\tfor a in ANIMAS:", "\t\t\t_by_name[a.name] = a.id", "\treturn _by_name.get(anima_name, 0)", "", "",
              "## 32x32 sprite for an anima id (cached).", "static func icon(id: int) -> AtlasTexture:",
              "\tif not _icons.has(id):", "\t\tvar t := AtlasTexture.new()", "\t\tt.atlas = load(ATLAS_PATH)",
              "\t\tt.region = Rect2(((id - 1) % ATLAS_COLUMNS) * CELL, ((id - 1) / ATLAS_COLUMNS) * CELL, CELL, CELL)",
              "\t\t_icons[id] = t", "\treturn _icons[id]", ""]
    with open(os.path.join(ROOT, "scripts/data/anima_roster.gd"), "w") as f:
        f.write("\n".join(lines))
    from collections import Counter
    c = Counter(t for a in animas for t in a["types"])
    print("animas:", len(animas), "| unique sprites:", len(hashes), "| families:", len(FAMILIES))
    print("type usage:", dict(c))
    print("ids:", {n: i + 1 for i, n in enumerate(names) if n in ("Cindle", "Brookit", "Sproutle", "Zaplet", "Nutkin", "Chirpa", "Snuffle", "Puffling", "Hopper", "Tadgle", "Fidget", "Bubblet", "Mossling", "Animus", "Pebblit")})


if __name__ == "__main__":
    main()
