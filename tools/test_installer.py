#!/usr/bin/env python3
"""Tests the Rust installer stub, the launcher, and the packer with a fake game (Linux/macOS).
Needs cargo. Usage:  python3 tools/test_installer.py"""
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRATE = ROOT / "installer"
fails = 0


def check(label, ok):
    global fails
    print(("PASS  " if ok else "FAIL  ") + label)
    fails += 0 if ok else 1


def run(*cmd, env=None, check_rc=False):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=60)


subprocess.run(["cargo", "build", "--release", "--quiet"], cwd=CRATE, check=True)
STUB, LAUNCH = CRATE / "target/release/animas-sfx", CRATE / "target/release/animas-launch"
tmp = pathlib.Path(tempfile.mkdtemp(prefix="animas-test-"))

# A fake "game": reports the environment it was started with and mimics Godot creating its user dir.
game = tmp / "fakegame"
game.write_text('#!/bin/sh\n'
                'echo "XDG_DATA_HOME=$XDG_DATA_HOME" > ../env.txt\necho "XDG_CONFIG_HOME=$XDG_CONFIG_HOME" >> ../env.txt\n'
                'echo "PORTABLE=$ANIMAS_PORTABLE" >> ../env.txt\necho "ARGS=$*" >> ../env.txt\n'
                'mkdir -p "$XDG_DATA_HOME/godot/app_userdata/Fake" && echo hi > "$XDG_DATA_HOME/godot/app_userdata/Fake/save.dat"\n'
                'echo started > ../launched.txt\n')
game.chmod(0o755)
out = tmp / "dist"
r = run(sys.executable, ROOT / "tools/package_portable.py", "--platform", "linux", "--game", game, "--launcher", LAUNCH, "--stub", STUB,
        "--out-dir", out, "--name", "test-linux", "--version", "9.9.9")
check("packer runs and writes both outputs", r.returncode == 0 and (out / "test-linux-setup.run").exists() and (out / "test-linux-portable.tar.gz").exists())
sfx = out / "test-linux-setup.run"
check("installer is the stub plus a payload", sfx.stat().st_size > STUB.stat().st_size + 400)
print("      stub %d KB, launcher %d KB, installer %d KB" % (STUB.stat().st_size // 1024, LAUNCH.stat().st_size // 1024, sfx.stat().st_size // 1024))

r = run(sfx, "--list")
check("--list shows the payload files", r.returncode == 0 and all(x in r.stdout for x in ("Animas Ember", "bin/AnimasEmber", "bin/.entry", ".launch", "data/README.txt")))
r = run(sfx, "--version")
check("--version prints the crate version", r.returncode == 0 and r.stdout.strip() == "0.1.0")

inst = tmp / "Installed Game"
r = run(sfx, "--yes", "--dir", inst)
check("installs with --yes --dir", r.returncode == 0 and "Done:" in r.stdout and (inst / "bin/.entry").read_text() == "AnimasEmber")
check("launcher and game keep their executable bit", os.access(inst / "Animas Ember", os.X_OK) and os.access(inst / "bin/AnimasEmber", os.X_OK))

# Launcher: all engine data goes under ./data and nothing lands in the (fake) home folder.
home = tmp / "home"
home.mkdir()
r = run(inst / "Animas Ember", "--hello", "world", env={"HOME": str(home), "PATH": "/usr/bin:/bin"})
env_txt = (inst / "env.txt").read_text() if (inst / "env.txt").exists() else ""
check("launcher starts the game and passes its arguments through", r.returncode == 0 and "ARGS=--hello world" in env_txt)
check("launcher redirects XDG_DATA_HOME into ./data", f"XDG_DATA_HOME={inst}/data/share" in env_txt and "PORTABLE=1" in env_txt)
check("the game's user data landed in ./data", (inst / "data/share/godot/app_userdata/Fake/save.dat").exists())
check("nothing was written to the home folder", list(home.iterdir()) == [])

# Update: game files are replaced, the data folder is kept.
(inst / "data/save1.txt").write_text("my progress")
(inst / "data/README.txt").write_text("edited by the player")
(inst / "bin/AnimasEmber").write_text("tampered")
r = run(sfx, "--yes", "--dir", inst)
check("update keeps saves and edited data files", (inst / "data/save1.txt").read_text() == "my progress" and (inst / "data/README.txt").read_text() == "edited by the player")
check("update replaces game files", (inst / "bin/AnimasEmber").read_text().startswith("#!/bin/sh") and "kept" in r.stdout)

# --run launches the game
(inst / "launched.txt").unlink()
r = run(sfx, "--yes", "--run", "--dir", inst)
time.sleep(1.0)
check("--run launches the game after installing", (inst / "launched.txt").exists())

# A bare stub has no payload
r = run(STUB, "--yes", "--dir", tmp / "nope")
check("bare stub refuses with a clear message", r.returncode == 1 and "bare installer stub" in r.stderr and not (tmp / "nope").exists())

# Damaged installers fail instead of installing garbage
data = bytearray(sfx.read_bytes())
data[STUB.stat().st_size + 2000:STUB.stat().st_size + 2016] = b"\xde\xad" * 8
(bad := tmp / "corrupt.run").write_bytes(bytes(data)); bad.chmod(0o755)
r = run(bad, "--yes", "--dir", tmp / "bad-install")
check("a corrupted payload is detected (non-zero exit, error shown)", r.returncode != 0 and "Error" in r.stderr)
(trunc := tmp / "trunc.run").write_bytes(sfx.read_bytes()[:-5000]); trunc.chmod(0o755)
r = run(trunc, "--yes", "--dir", tmp / "trunc-install")
check("a truncated installer is rejected", r.returncode != 0)

# Zip-slip: entries that escape the install folder are skipped
evil = tmp / "evil.zip"
with zipfile.ZipFile(evil, "w") as z:
    z.writestr("../escaped.txt", "x"); z.writestr("/abs_escaped_animas.txt", "x"); z.writestr("fine/ok.txt", "ok"); z.writestr(".launch", "x")
payload = evil.read_bytes()
(evilsfx := tmp / "evil.run").write_bytes(STUB.read_bytes() + payload + struct.pack("<Q", len(payload)) + b"ANIMASFX"); evilsfx.chmod(0o755)
slip = tmp / "slip" / "target"
r = run(evilsfx, "--yes", "--dir", slip)
check("zip-slip entries are not extracted outside the folder",
      (slip / "fine/ok.txt").exists() and not (slip.parent / "escaped.txt").exists() and not pathlib.Path("/abs_escaped_animas.txt").exists())

# Launcher error paths
lonely = tmp / "lonely"
lonely.mkdir()
shutil.copy(LAUNCH, lonely / "Animas Ember")
r = run(lonely / "Animas Ember")
check("launcher explains a missing game instead of crashing", r.returncode == 1 and "missing" in r.stderr)

shutil.rmtree(tmp, ignore_errors=True)
print("\nRESULT: " + ("ALL PASSED" if not fails else f"{fails} FAILED"))
sys.exit(1 if fails else 0)
