"""Build a browser-playable (WebAssembly) version with pygbag.

Pygbag compiles the game to run in the browser via CPython-on-WASM. Because
pygbag packages the *whole* folder it's pointed at, we first stage only the
runtime files into ``web_build/`` (no dev tools, no 18 MB .exe, no backups),
then build that. The result lands in ``web_build/build/web/`` — zip that folder
(with ``index.html`` at the zip root) and upload it to itch.io as an HTML5 game,
ticking "This file will be played in the browser".

    python build_web.py            # stage + build
    python build_web.py --serve    # stage + build + open a local test server

Run native instead with:  python main.py
Build the Windows .exe with:  python build.py
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STAGE = os.path.join(ROOT, "web_build")

# Python modules that are dev/build tooling, not part of the runtime.
SKIP_PY = {
    "build.py", "build_web.py", "make_art.py", "make_audio.py",
    "promo.py", "shot.py", "test_smoke.py",
}

# Asset folders to ship (subpaths to skip inside them).
ASSET_DIRS = {
    "textures": {"_original"},   # drop the pre-edit sprite backups
    "fonts": set(),
    "sounds": set(),
}
SKIP_FILES = {"README.md"}       # docs that needn't ship inside asset folders
# Browsers/pygbag don't support mp3 — we ship the .ogg conversions instead
# (sound._find prefers .ogg anyway). mp3s are kept for the desktop build.
SKIP_EXTS = (".mp3",)


def _ignore(skip_subdirs):
    def _fn(_dir, names):
        return [n for n in names
                if n in skip_subdirs or n in SKIP_FILES
                or n.lower().endswith(SKIP_EXTS)]
    return _fn


def stage():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    for name in os.listdir(ROOT):
        if name.endswith(".py") and name not in SKIP_PY:
            shutil.copy2(os.path.join(ROOT, name), os.path.join(STAGE, name))

    for folder, skip in ASSET_DIRS.items():
        src = os.path.join(ROOT, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(STAGE, folder), ignore=_ignore(skip))

    print("Staged runtime files into", STAGE)


def build(serve):
    main_py = os.path.join(STAGE, "main.py")
    cmd = [sys.executable, "-m", "pygbag",
           "--app_name", "TimeTravellersDilemma",
           "--title", "Time Traveller's Dilemma",
           "--ume_block", "0"]          # no extra "click to start" gate
    if not serve:
        cmd.append("--build")        # build only; don't start a server
    cmd.append(main_py)
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def patch_autostart():
    """pygbag 0.9.3's default template hard-waits on a user-gesture flag
    (`platform.window.MM.UME`) before it ever runs main.py — and that flag
    isn't reliably set by a click inside itch's iframe, so the game hangs on a
    grey screen forever. Neutralise that wait so the game auto-starts; audio
    just unlocks on the first key/click instead (browsers require a gesture for
    sound, but the game itself runs immediately)."""
    index = os.path.join(STAGE, "build", "web", "index.html")
    with open(index, "r", encoding="utf-8") as f:
        html = f.read()
    needle = "if not platform.window.MM.UME:"
    repl = "if False:  # pygbag UME gate disabled by build_web.py — autostart"
    if needle in html:
        html = html.replace(needle, repl, 1)
        with open(index, "w", encoding="utf-8") as f:
            f.write(html)
        print("Patched index.html: UME wait removed (auto-start enabled)")
    else:
        print("WARNING: UME wait pattern not found — pygbag template may have "
              "changed. The game may require a click to start.")


def main():
    serve = "--serve" in sys.argv
    stage()
    build(serve)
    patch_autostart()
    out = os.path.join(STAGE, "build", "web")
    if not serve:
        print("\nWeb build complete.")
        print("Output folder:", out)
        print("Zip the CONTENTS of that folder (index.html at the zip root)")
        print("and upload to itch.io as an HTML5 game.")


if __name__ == "__main__":
    main()
