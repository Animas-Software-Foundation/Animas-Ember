#!/usr/bin/env python3
"""Stamps the version from the VERSION file into project.godot and export_presets.cfg.

  python3 tools/sync_version.py           rewrite the files
  python3 tools/sync_version.py --check   exit 1 if they are out of date (no changes)

VERSION holds plain semver such as 0.0.1 or 1.2.0-beta.1. Android's integer
version code is major*1,000,000 + minor*1,000 + patch (0.0.1 -> 1, 1.2.3 -> 1,002,003).
Platform fields that must be purely numeric (macOS, Windows) get the core x.y.z only.
"""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
version = (root / "VERSION").read_text().strip()
m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?", version)
if not m:
    sys.exit(f"VERSION '{version}' is not semver (expected e.g. 1.2.3 or 1.2.3-beta.1)")
major, minor, patch = (int(x) for x in m.groups()[:3])
core = f"{major}.{minor}.{patch}"
code = major * 1_000_000 + minor * 1_000 + patch

RULES = {
    "project.godot": [(r'(config/version=")[^"]*(")', version)],
    "installer/Cargo.toml": [(r'(?m)^(version = ")[^"]*(")', core)],
    "installer/Cargo.lock": [(r'(name = "animas-installer"\nversion = ")[^"]*(")', core)],
    "installer-gui/Cargo.toml": [(r'(?m)^(version = ")[^"]*(")', core)],
    "installer-gui/Cargo.lock": [(r'(name = "animas-setup"\nversion = ")[^"]*(")', core)],
    "export_presets.cfg": [
        (r'(version/name=")[^"]*(")', version),
        (r'(application/short_version=")[^"]*(")', core),
        (r'(application/version=")[^"]*(")', core),
        (r'(application/file_version=")[^"]*(")', core),
        (r'(application/product_version=")[^"]*(")', core),
    ],
}
stale = []
for name, rules in RULES.items():
    path = root / name
    text = path.read_text()
    new = text
    for pattern, value in rules:
        new = re.sub(pattern, lambda mo, v=value: mo.group(1) + v + mo.group(2), new)
    if name == "export_presets.cfg":
        new = re.sub(r"(version/code=)\d+", lambda mo: mo.group(1) + str(code), new)
    if new != text:
        stale.append(name)
        if "--check" not in sys.argv:
            path.write_text(new)

if "--check" in sys.argv:
    if stale:
        sys.exit("Out of date with VERSION: " + ", ".join(stale) + "  (run: python3 tools/sync_version.py)")
    print(f"OK: version {version} (android code {code})")
else:
    print(f"Version {version} (android code {code}); updated: {', '.join(stale) or 'nothing, already in sync'}")
