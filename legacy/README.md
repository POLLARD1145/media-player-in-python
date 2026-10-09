# Pd Player (Legacy Python Edition)
![v1.0.0 MacOS UI](/assets/images/screenshots/v1.0.0-macOS.png)

A desktop media player for macOS and Windows built with PySide6 (Qt), pygame-ce,
and Qt Multimedia.

## Download

**macOS (Apple Silicon):**
[PdPlayer-v1.0.0-macOS-arm64.dmg](https://github.com/POLLARD1145/media-player-in-python/releases/latest/download/PdPlayer-v1.0.0-macOS-arm64.dmg)

Open the DMG, drag **Pd Player** onto **Applications**, then launch.
First launch: right-click → Open (unsigned build). If macOS reports the app as
"damaged", run `xattr -cr "/Applications/Pd Player.app"` in Terminal.

> **Note:** This is the legacy implementation. A cross-platform Flutter rewrite
> (desktop + iOS) lives in the repository root.

## Features

- **Audio playback** — MP3, WAV, OGG, FLAC, AAC, M4A (pygame-ce)
- **Video playback** — MP4, MKV, AVI, MOV, WMV, FLV (Qt Multimedia / FFmpeg),
  embedded in the main window with audio
- **Seek bar** — click anywhere to jump, drag to scrub, works for video
- **Repeat modes** — Off / Repeat All / Repeat One (auto-advances playlists)
- **Fullscreen video** — floating auto-hiding control bar with seek, play/pause,
  stop, and exit; tiny corner handle to restore
- **Subtitles** — auto-loads `.srt`/`.vtt` files matching the video name,
  embedded track selection for MKV/MP4, manual file loading
- **Recent media** — remembers recent folders and files (Media → Recent Media),
  persisted in `~/.pd_player_recent.json`
- **Library browsing** — Music library, Video library, folder browsing, search
- **Custom app icon** — bundled `.icns` in the macOS build

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play / Pause |
| S | Stop |
| R | Cycle repeat mode (Off → All → One) |
| F | Fullscreen (while video is showing) |
| Esc | Exit fullscreen |
| ← / → | Seek video -10s / +10s |
| Double-click video | Toggle fullscreen |

## Run From Source

### Requirements

- Python 3.10+ (3.12 recommended — PySide6 6.12 needs it)
- macOS or Windows

### macOS

```bash
cd legacy

# Easiest: uv (installs its own Python, no admin needed)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# Or with system Python 3.12+
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
.venv/bin/python mplayer_optimized.py
```

### Windows

```powershell
cd legacy

# Install Python 3.12 from python.org first, then:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run
python mplayer_optimized.py
```

## Release File Naming

All release assets follow `PdPlayer-v<version>-<os>-<arch>.<ext>` so users can
identify the right download at a glance:

| Platform | Format | Example |
|----------|--------|---------|
| Windows | `PdPlayer-v1.0.0-windows-x64.exe` (portable) or `.msi` (installer) | |
| macOS | `PdPlayer-v1.0.0-macOS-arm64.dmg` (Apple Silicon) / `-x64` (Intel) | |
| Linux | `PdPlayer-v1.0.0-linux-amd64.tar.gz` | |

Version comes from `APP_VERSION` in `mplayer_optimized.py` — bump it there,
stamp the bundle (below), then name the DMG/installer to match the git tag.

## Build a Standalone Executable

### macOS (.app)

```bash
cd legacy
.venv/bin/pip install pyinstaller   # or: uv pip install --python .venv/bin/python pyinstaller

# Generate the .icns icon (once)
mkdir -p /tmp/pd.iconset
for s in 16 32 64 128 256 512 1024; do
  sips -z $s $s "../assets/images/logo/Pd Player Logo.png" --out "/tmp/pd.iconset/icon_${s}x${s}.png"
done
iconutil -c icns /tmp/pd.iconset -o /tmp/pd_player.icns

# Build
.venv/bin/pyinstaller --noconfirm --windowed \
  --name "Pd Player" \
  --icon /tmp/pd_player.icns \
  --add-data "../assets:assets" \
  mplayer_optimized.py

# Result: dist/Pd Player.app  (~146MB)

# Optional: package as a distributable DMG installer
mkdir -p /tmp/pd_dmg
cp -R "dist/Pd Player.app" /tmp/pd_dmg/
ln -s /Applications /tmp/pd_dmg/Applications
hdiutil create -volname "Pd Player" -srcfolder /tmp/pd_dmg -ov -format UDZO "dist/PdPlayer-v1.0.0-macOS-arm64.dmg"

# Result: dist/PdPlayer-v1.0.0-macOS-arm64.dmg — users drag the app onto /Applications to install
```

After building, stamp the bundle version (PyInstaller defaults it to 0.0.0):

```bash
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString 1.0.0" \
  -c "Set :CFBundleVersion 1.0.0" "dist/Pd Player.app/Contents/Info.plist"
```

First launch may require right-click → Open (unsigned app, Gatekeeper).

### Windows (.exe / installer)

PyInstaller does not cross-compile — run this **on a Windows machine**:

```powershell
cd legacy
pip install pyinstaller

# Portable single-file exe
pyinstaller --noconfirm --windowed --onefile `
  --name "PdPlayer" `
  --icon "..\assets\images\logo\PdPlayer.ico" `
  --add-data "..\assets;assets" `
  mplayer_optimized.py

# Result: dist\PdPlayer.exe → rename to PdPlayer-v1.0.0-windows-x64.exe
```

Convert the PNG logo to `.ico` first — e.g. with ImageMagick
`magick "Pd Player Logo.png" -define icon:auto-resize "PdPlayer.ico"`.

For a real installer (Start Menu entry, uninstaller, install dir choice),
build the folder version (`--onedir`, the default without `--onefile`) and wrap
it with [Inno Setup](https://jrsoftware.org/isinfo.php) (free) or WiX:

```powershell
pyinstaller --noconfirm --windowed `
  --name "Pd Player" `
  --icon "..\assets\images\logo\PdPlayer.ico" `
  --add-data "..\assets;assets" `
  mplayer_optimized.py
# Point Inno Setup at dist\Pd Player\ → produces PdPlayer-v1.0.0-windows-x64-setup.exe
```

## Project Structure

```
legacy/
├── mplayer_optimized.py   # Main application (run this)
├── mplayer.py             # Original version (reference only)
├── audio_controller.py    # Audio playback (pygame-ce)
├── video_player.py        # Video playback + subtitle parsing (Qt Multimedia)
├── media_manager.py       # File discovery / library scanning
├── requirements.txt       # Dependencies
└── test_modules.py        # Module smoke tests

assets/images/logo/        # App icon (PNG + SVG)
```

## Files the App Writes

- `media_player.log` — runtime log (working directory)
- `~/.pd_player_recent.json` — recent media list

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'PySide6'` | Activate the venv first |
| Video has no sound | Use `mplayer_optimized.py` — the original `mplayer.py`/old code used OpenCV which cannot decode audio |
| Subtitles not showing | Ensure the `.srt` has the same filename as the video, or use Playback → Subtitles → Load Subtitle File |
| App won't open on macOS | Right-click → Open (unsigned build) |
| Something else | Check `media_player.log` |

## Developer

**POLLARD SAMBA** — POLLADSAMBA1@GMAIL.COM — GitHub: POLLARD1145
