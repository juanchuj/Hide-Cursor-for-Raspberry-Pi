# Hide Cursor for Raspberry Pi

Make the mouse pointer invisible on Raspberry Pi OS, for kiosks, digital signage and video installations such as
[Adafruit Video Looper 2](https://github.com/adafruit/pi_video_looper2).

## The problem

Video players usually hide the cursor only inside their own window. When a new window opens, for example when
Video Looper 2 starts the next video in VLC, the system pointer comes back and sits on top of the picture, often in
a corner of the screen or projection.

## How it works

`hide_cursor.py` installs a **fully transparent cursor theme** and makes it the default:

- for the **labwc** desktop (Wayland) and every app it starts, via `~/.config/labwc/environment`
- for **X11 / Xwayland apps** that run outside the desktop session, such as Video Looper 2's VLC and pygame windows,
  via `~/.icons/default`

Any window that sets a cursor gets an invisible one. Nothing in your video player is changed, and the mouse keeps
working, you just cannot see the pointer.

## Requirements

- Raspberry Pi OS with the default **labwc** desktop (current Raspberry Pi OS releases).
- Python 3 (included with Raspberry Pi OS). No extra packages.

Tested on a Raspberry Pi 4 with 64-bit Raspberry Pi OS (labwc desktop), together with Adafruit Video Looper 2.

To check your desktop: `ps -e | grep -E "labwc|wayfire|Xorg"`. With Wayfire or X11 the labwc part does nothing,
although X11 apps still pick up the transparent default theme.

## Install

```bash
git clone https://github.com/juanchuj/Hide-Cursor-for-Raspberry-Pi
cd Hide-Cursor-for-Raspberry-Pi
python3 hide_cursor.py
sudo reboot
```

Run it as the user that is logged in to the desktop, **without** `sudo`.

## Undo

```bash
python3 hide_cursor.py --undo
sudo reboot
```

This removes the transparent theme, restores any previous `~/.icons/default/index.theme`, and removes the
`XCURSOR_THEME` line it added. Other lines in your labwc environment file are left alone.

## Using the desktop while the cursor is hidden

The pointer is invisible on the desktop too. Options:

- Manage the Pi over SSH, which is not affected.
- Use keyboard shortcuts: Super opens the menu, Alt+Tab switches windows, Ctrl+Alt+T opens a terminal.
- Temporarily restore it: `python3 hide_cursor.py --undo && sudo systemctl restart lightdm`, and hide it again the
  same way afterwards.

The change only takes effect when the desktop session starts, so a reboot or a `lightdm` restart is always needed.

## What it changes

| Path | Change |
|---|---|
| `~/.icons/transparent/` | New theme: a 1×1 transparent cursor, linked under 76 common cursor names |
| `~/.icons/default/index.theme` | Inherits the transparent theme (an existing file is backed up as `.bak`) |
| `~/.config/labwc/environment` | Adds `XCURSOR_THEME=transparent` |

Running it twice is safe; nothing is duplicated.

## License

MIT, see [LICENSE](LICENSE).
