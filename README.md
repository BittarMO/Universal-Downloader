# 🎵 Universal Downloader

A modern and easy-to-use video and audio downloader built with Python.

**Universal Downloader** supports **YouTube and 20+ other websites** using yt-dlp and FFmpeg – including SoundCloud, Vimeo, Twitch, TikTok, Twitter (X), Facebook, Instagram, Bilibili, Rumble and many more.

---

## ✨ Features

- Download audio as **MP3 up to 320 kbps**
- Download video as **MP4 in best quality**
- **Playlist support** – each video becomes a queue item
- **Download queue system** – add multiple links and process them in order
- **Automatic retry** on network errors (up to 2 attempts)
- **Real-time progress** with speed and ETA
- **Download history** – track past downloads
- **Automatic installation** of required tools on all platforms (yt-dlp, FFmpeg)
- **Supports 20+ websites** (not just YouTube)
- Simple and modern user interface
- Multi‑platform support (Windows native, Linux/macOS via source)

---

## 💻 Requirements

### Windows

- Windows 10 or Windows 11
- Internet connection
- **500 MB free disk space**

### Linux / macOS

- Python 3.10+
- Internet connection
- **500 MB free disk space**
- `xz-utils` (Linux only – for extracting FFmpeg)

> ℹ️ On Linux/macOS, the app will automatically download `yt-dlp` and `FFmpeg` on first launch if they are missing.

---

## 🚀 Installation

### Windows (Portable)

1. Download `Universal Downloader.exe` from the [Releases](../../releases) page.
2. Run the `.exe` file directly – no installation required.
3. On first launch, the app will download `yt-dlp` and `FFmpeg` (approx. 150 MB).

> ⚠️ **Windows SmartScreen** may show a warning. Click **More info** → **Run anyway** – this is normal for unsigned applications.

### Linux

# Clone the repository

git clone https://github.com/BittarMO/Universal-Downloader.git
cd Universal-Downloader

# Run the application

python3 Code/Universal_Downloader.py
The app will download missing tools on first run.

macOS

# Clone the repository

git clone https://github.com/BittarMO/Universal-Downloader.git
cd Universal-Downloader

# Run the application

python3 Code/Universal_Downloader.py
📥 Usage
Copy a video or playlist link from any supported website (YouTube, TikTok, Twitter, SoundCloud, …)

Paste it into Universal Downloader (right-click or Ctrl+V)

Select MP3 or MP4

Click Add

Click Start Queue

Downloads are processed automatically in the order you added them.

🌐 Supported Websites (20+)
YouTube

SoundCloud

Vimeo

Dailymotion

Twitch

X (Twitter)

Reddit

Facebook

Instagram

TikTok

Bilibili

Rumble

… and many more via yt-dlp

Note: Some sites may require login or have geo‑restrictions.

❓ FAQ
Is it free?
Yes, completely free and ad‑free.

Where are files saved?
Format Default location
MP3 Downloads\Universal Downloader\Music
MP4 Downloads\Universal Downloader\Videos
Can I change the folder?
Yes. Click the 📁 folder icon inside the app and choose a new location.

Why does a download fail?
Possible reasons:

No internet connection

Private or deleted video

Age‑restricted content

Geo‑blocking

Not enough disk space (needs at least 500 MB)

Login required for some sites

Does it work on Linux or macOS?
Yes, via source code. The app will download all required tools on first launch.

What if I decline the automatic tool installation?
The app will close. Restart it anytime – it will ask again.

🛠 Technologies
Python

yt-dlp (supports 20+ websites)

FFmpeg

CustomTkinter

📞 Contact
Developer: Bittar Tech Lab
Email: bittarmohamad023@gmail.com
GitHub: https://github.com/BittarMO/Universal-Downloader

💚 Support
If you like Universal Downloader, you can support the project voluntarily via PayPal:

https://www.paypal.com/paypalme/mohamadbittar

📄 License
Free for personal use only.

✅ Allowed:
Personal use

Sharing with friends and family

❌ Not allowed:
Commercial use

Selling the software

Redistribution or modification without permission

Made with ❤️ by Bittar Tech Lab
Version 1.0 • June 2026
