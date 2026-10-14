#!/usr/bin/env python3
"""
hide_cursor.py - make the mouse pointer invisible on Raspberry Pi OS (labwc / Wayland + Xwayland).

Creates a transparent cursor theme in ~/.icons/transparent, makes it the default
theme for X11 apps (VLC/pygame used by Video Looper) and for labwc itself.
No changes to Video Looper.

Usage (as your normal user, NOT sudo):
    python3 hide_cursor.py          # install, then reboot
    python3 hide_cursor.py --undo   # restore the normal cursor, then reboot
"""
import os
import shutil
import struct
import sys

HOME = os.path.expanduser("~")
THEME_DIR = os.path.join(HOME, ".icons", "transparent")
CURSOR_DIR = os.path.join(THEME_DIR, "cursors")
DEFAULT_DIR = os.path.join(HOME, ".icons", "default")
LABWC_ENV = os.path.join(HOME, ".config", "labwc", "environment")
MARK = "# hide_cursor.py"

# Cursor names used by X11 / Wayland apps; all point to the same transparent image.
NAMES = """left_ptr default arrow top_left_arrow pointer hand hand1 hand2 pointing_hand
xterm text ibeam watch wait left_ptr_watch progress half-busy crosshair cross tcross
move fleur all-scroll grab grabbing openhand closedhand dnd-move dnd-copy dnd-link
dnd-none copy alias no-drop not-allowed forbidden circle help question_arrow
context-menu cell vertical-text col-resize row-resize ew-resize ns-resize nesw-resize
nwse-resize n-resize s-resize e-resize w-resize ne-resize nw-resize se-resize sw-resize
sb_h_double_arrow sb_v_double_arrow h_double_arrow v_double_arrow size_hor size_ver
size_bdiag size_fdiag size_all top_side bottom_side left_side right_side top_left_corner
top_right_corner bottom_left_corner bottom_right_corner zoom-in zoom-out X_cursor""".split()


def xcursor_file():
    """Minimal Xcursor file: one 1x1 fully transparent image per nominal size."""
    sizes = [16, 24, 32, 48, 64]
    header_len, toc_len, img_hdr = 16, 12, 36
    img_len = img_hdr + 4                      # 1 pixel ARGB
    out = struct.pack("<4sIII", b"Xcur", header_len, 0x10000, len(sizes))
    pos = header_len + toc_len * len(sizes)
    for s in sizes:
        out += struct.pack("<III", 0xFFFD0002, s, pos)
        pos += img_len
    for s in sizes:
        out += struct.pack("<IIIIIIIII", img_hdr, 0xFFFD0002, s, 1, 1, 1, 0, 0, 0)
        out += struct.pack("<I", 0x00000000)   # transparent pixel
    return out


def install():
    os.makedirs(CURSOR_DIR, exist_ok=True)
    data = xcursor_file()
    base = os.path.join(CURSOR_DIR, "left_ptr")
    with open(base, "wb") as f:
        f.write(data)
    for n in NAMES:
        p = os.path.join(CURSOR_DIR, n)
        if n != "left_ptr" and not os.path.lexists(p):
            os.symlink("left_ptr", p)
    with open(os.path.join(THEME_DIR, "index.theme"), "w") as f:
        f.write("[Icon Theme]\nName=transparent\nComment=Invisible cursor\n")

    # X11 apps without XCURSOR_THEME set (e.g. the looper service) use ~/.icons/default
    os.makedirs(DEFAULT_DIR, exist_ok=True)
    idx = os.path.join(DEFAULT_DIR, "index.theme")
    if os.path.exists(idx) and not os.path.exists(idx + ".bak"):
        shutil.copy2(idx, idx + ".bak")
    with open(idx, "w") as f:
        f.write(f"{MARK}\n[Icon Theme]\nInherits=transparent\n")

    # labwc and the apps it starts
    os.makedirs(os.path.dirname(LABWC_ENV), exist_ok=True)
    lines = open(LABWC_ENV).read().splitlines() if os.path.exists(LABWC_ENV) else []
    lines = [l for l in lines if not l.startswith("XCURSOR_THEME=")]
    lines.append("XCURSOR_THEME=transparent")
    with open(LABWC_ENV, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Invisible cursor installed. Reboot to apply:  sudo reboot")


def undo():
    shutil.rmtree(THEME_DIR, ignore_errors=True)
    idx = os.path.join(DEFAULT_DIR, "index.theme")
    if os.path.exists(idx) and open(idx).read().startswith(MARK):
        os.remove(idx)
        if os.path.exists(idx + ".bak"):
            os.rename(idx + ".bak", idx)
    if os.path.exists(LABWC_ENV):
        lines = [l for l in open(LABWC_ENV).read().splitlines()
                 if l.strip() != "XCURSOR_THEME=transparent"]
        with open(LABWC_ENV, "w") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))
    print("Normal cursor restored. Reboot to apply:  sudo reboot")


if __name__ == "__main__":
    if os.geteuid() == 0:
        sys.exit("Run as your normal user (without sudo).")
    undo() if "--undo" in sys.argv else install()
