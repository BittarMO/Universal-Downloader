# Universal Downloader

> A modern, cross-platform video and audio downloader built with Python.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/BittarMO/Universal-Downloader/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#-installation)
[![License](https://img.shields.io/badge/license-Personal%20Use-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)](https://www.python.org/)

---

## Overview

**Universal Downloader** lets you save videos and audio from YouTube and 20+ other platforms with a clean, minimal interface. It handles tool installation automatically — no manual setup required.

Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [FFmpeg](https://ffmpeg.org/).

---

## Features

| Feature | Details |
|---|---|
| 🎵 Audio | MP3 export up to 320 kbps |
| 🎬 Video | MP4 in best available quality |
| 📋 Queue | Add multiple links, processed in order |
| 🔁 Retry | Automatic retry on network failure (up to 2 attempts) |
| 📊 Progress | Real-time speed and ETA display |
| 📜 History | Persistent download history |
| 🌐 Sites | 20+ supported platforms via yt-dlp |
| 🔧 Auto-setup | yt-dlp and FFmpeg installed automatically on first run |

---

## Supported Platforms

YouTube · SoundCloud · Vimeo · Dailymotion · Twitch · X (Twitter) · Reddit · Facebook · Instagram · TikTok · Bilibili · Rumble · and many more via yt-dlp.

> Some platforms may require login credentials or have geo-restrictions.

---

## Requirements

### Windows
- Windows 10 or 11 (64-bit)
- Active internet connection
- 500 MB free disk space

### Linux / macOS
- Python 3.10 or higher
- Active internet connection
- 500 MB free disk space
- `xz-utils` (Linux only — required for FFmpeg extraction)

---

## Installation

### Windows — Portable Executable

1. Download `Universal_Downloader_Setup.exe` from the [Releases](../../releases) page.
2. Run the file directly — no installation required.
3. On first launch, yt-dlp and FFmpeg will be downloaded automatically (~150 MB).

> **Windows SmartScreen warning:** Click **More info → Run anyway**. This is expected for unsigned applications.

### Linux / macOS — From Source

```bash
# Clone the repository
git clone https://github.com/BittarMO/Universal-Downloader.git
cd Universal-Downloader

# (Optional) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Run the application
python3 tools_data/universal_downloader.py
```

Missing tools (yt-dlp, FFmpeg) will be downloaded automatically on first run.

---

## Usage

1. Copy a video or playlist URL from any supported site.
2. Paste it into the app (`Ctrl+V` or right-click).
3. Select **MP3** or **MP4**.
4. Click **Add** to queue the item.
5. Click **Start Queue** — downloads are processed in order.

### Default Save Locations

| Format | Default Path |
|--------|-------------|
| MP3 | `Downloads\Universal Downloader\Music` |
| MP4 | `Downloads\Universal Downloader\Videos` |

> To change the folder, click the 📁 icon inside the app.

---

## Project Structure

```
Universal-Downloader/
├── tools_data/
│   ├── universal_downloader.py   # Main application
│   ├── get_version.py            # Version reader (build-time safe)
│   ├── Universal_Downloader.spec # PyInstaller build spec
│   └── universal.ico             # Application icon
├── version.json                  # Version metadata
├── .gitignore
└── README.md
```

---

## Building from Source (Windows)

```bash
pip install pyinstaller customtkinter

cd tools_data
pyinstaller Universal_Downloader.spec
```

The output executable will be placed in `dist/`.

---

## FAQ

**Is it free?**
Yes, completely free and ad-free for personal use.

**Why does a download fail?**
Common causes: no internet, private or deleted video, age restriction, geo-block, insufficient disk space (<500 MB), or login required.

**What if I decline tool installation on first launch?**
The app will exit. Restart it anytime — it will prompt again.

**Does it work on Linux or macOS?**
Yes, via source. All required tools are downloaded automatically on first run.

---

## Technologies

- [Python 3.10+](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [PyInstaller](https://pyinstaller.org/) (Windows build)

---

## License

Free for **personal use only**.

| ✅ Allowed | ❌ Not Allowed |
|---|---|
| Personal use | Commercial use |
| Sharing with friends and family | Selling the software |
| | Redistribution or modification without permission |

---

## Support

If you find this project useful, consider supporting it:

[![PayPal](https://img.shields.io/badge/Support-PayPal-blue.svg)](https://www.paypal.com/paypalme/mohamadbittar)

---

## Contact

**Developer:** Bittar Tech Lab
**Email:** bittarmohamad023@gmail.com
**GitHub:** [github.com/BittarMO/Universal-Downloader](https://github.com/BittarMO/Universal-Downloader)

---

*Version 1.0.0 — June 2026 — Made with ❤️ by Bittar Tech Lab*
