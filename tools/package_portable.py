#!/usr/bin/env python3
"""Packages an exported game as a portable archive and a self-extracting installer.

For one platform it produces, in --out-dir:
  <name>-portable.zip|.tar.gz   the game folder: launcher + bin/ + data/
  <name>-setup.exe|.run         SFX installer = animas-sfx stub + that folder as a zip + trailer

The folder layout (what the launcher in installer/src/launch.rs expects):
  Animas Ember[.exe]   the launcher (redirects AppData to ./data, then starts the game)
  bin/                 the exported Godot game, plus bin/.entry naming the executable inside it
  data/                saves and settings (the installer never overwrites this)

Usage:
  python3 tools/package_portable.py --platform linux --game build/AnimasEmber-linux-x86_64.x86_64 \\
      --launcher installer/target/release/animas-launch --stub installer/target/release/animas-sfx \\
      --out-dir dist --name animas-ember-v0.1.0-linux-x86_64 --version 0.1.0
macOS: --game is the exported .zip (it contains the .app).
"""
import argparse
import io
import os
import struct
import sys
import tarfile
import zipfile

MAGIC = b"ANIMASFX"
FOLDER = "Animas Ember"
STAMP = (2026, 1, 1, 0, 0, 0)  # fixed timestamp so packaging is reproducible


def build_entries(platform, game, launcher, version):
    """-> (list of (arcname, bytes, mode), launcher arcname)"""
    launch_name = FOLDER + (".exe" if platform == "windows" else "")
    entries = [(launch_name, open(launcher, "rb").read(), 0o755)]
    if platform == "windows":
        entries += [("bin/AnimasEmber.exe", open(game, "rb").read(), 0o755), ("bin/.entry", b"AnimasEmber.exe", 0o644)]
    elif platform == "linux":
        entries += [("bin/AnimasEmber", open(game, "rb").read(), 0o755), ("bin/.entry", b"AnimasEmber", 0o644)]
    elif platform == "macos":
        entry = None
        with zipfile.ZipFile(game) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                mode = (info.external_attr >> 16) & 0o7777 or 0o644
                if "/Contents/MacOS/" in info.filename:
                    mode, entry = 0o755, info.filename
                entries.append(("bin/" + info.filename, z.read(info), mode))
        if not entry:
            sys.exit("no Contents/MacOS executable found in the macOS export")
        entries.append(("bin/.entry", entry.encode(), 0o644))
    else:
        sys.exit("unknown platform " + platform)
    readme = (f"Animas: Ember {version}\n\nRun \"{launch_name}\" to play.\n\n"
              "This is a portable install: your saves and settings are kept in the \"data\" folder next to the game,\n"
              "and nothing is written to AppData or your home folder. To move the game to another computer or a USB stick,\n"
              "copy this whole folder. To uninstall, delete it.\n\nhttps://github.com/pixel-pulse-games/Animas-Ember\n")
    entries += [
        (".launch", launch_name.encode(), 0o644),
        ("README.txt", readme.encode(), 0o644),
        ("data/README.txt", b"Your saves and settings for Animas: Ember are stored in this folder.\n"
                            b"Copy the whole game folder, including this one, to take your progress with you.\n", 0o644),
    ]
    return entries


def make_zip(entries, prefix=""):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data, mode in entries:
            info = zipfile.ZipInfo(prefix + name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, so permissions are kept
            info.external_attr = (0o100000 | mode) << 16
            z.writestr(info, data)
    return buf.getvalue()


def make_targz(entries, path, prefix):
    with tarfile.open(path, "w:gz", compresslevel=9) as t:
        for name, data, mode in entries:
            info = tarfile.TarInfo(prefix + name)
            info.size, info.mode, info.mtime, info.uname, info.gname = len(data), mode, 1767225600, "", ""
            t.addfile(info, io.BytesIO(data))


def make_sfx(stub_path, payload):
    return open(stub_path, "rb").read() + payload + struct.pack("<Q", len(payload)) + MAGIC


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--platform", required=True, choices=["windows", "linux", "macos"])
    ap.add_argument("--game", required=True)
    ap.add_argument("--launcher", required=True)
    ap.add_argument("--stub", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--version", default="0.0.0")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    entries = build_entries(a.platform, a.game, a.launcher, a.version)

    prefix = FOLDER + "/"
    if a.platform == "linux":
        portable = os.path.join(a.out_dir, a.name + "-portable.tar.gz")
        make_targz(entries, portable, prefix)
    else:
        portable = os.path.join(a.out_dir, a.name + "-portable.zip")
        open(portable, "wb").write(make_zip(entries, prefix))
    setup = os.path.join(a.out_dir, a.name + ("-setup.exe" if a.platform == "windows" else "-setup.run"))
    open(setup, "wb").write(make_sfx(a.stub, make_zip(entries)))
    os.chmod(setup, 0o755)
    for p in (portable, setup):
        print("wrote %s (%.1f MB)" % (p, os.path.getsize(p) / 1048576))


if __name__ == "__main__":
    main()
