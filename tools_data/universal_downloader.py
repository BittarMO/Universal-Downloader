# ══════════════════════════════════════════════════════════════════════════════
#  §0  STDLIB & THIRD-PARTY IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
import zipfile

from dataclasses import dataclass, field
from enum        import Enum
from typing      import Any, Callable, Dict, List, NamedTuple, Optional, Tuple


# ══════════════════════════════════════════════════════════════════════════════
#  §1  LOGGING & PLATFORM DETECTION
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level  = logging.WARNING,
    format = "%(levelname)s [%(name)s]: %(message)s",
)
log = logging.getLogger(__name__)

IS_WINDOWS : bool = platform.system() == "Windows"
IS_LINUX   : bool = platform.system() == "Linux"
IS_MAC     : bool = platform.system() == "Darwin"

if IS_LINUX or IS_MAC:
    import signal as _signal


# ══════════════════════════════════════════════════════════════════════════════
#  §2  PATHS & GLOBAL CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

IS_FROZEN : bool = getattr(sys, "frozen", False)


def resolve_resource_path(relative: str) -> str:
    """Return the absolute path for a bundled resource when the app is frozen."""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative)



def get_base_data_dir() -> str:
    if IS_FROZEN:
        return os.path.join(sys._MEIPASS, "tools_data")
    else:
        return os.path.dirname(os.path.abspath(__file__))


# ── Directory & binary paths ──────────────────────────────────────────────────

BASE_DATA_DIR     : str = get_base_data_dir()
ICON_PATH         : str = os.path.join(BASE_DATA_DIR, "universal.ico")

YT_DLP_BINARY     : str = "yt-dlp.exe"   if IS_WINDOWS else "yt-dlp"
FFMPEG_BINARY     : str = "ffmpeg.exe"   if IS_WINDOWS else "ffmpeg"

BASE_DOWNLOAD_DIR : str = os.path.join(os.path.expanduser("~"), "Downloads", "Universal Downloader")
DEFAULT_MUSIC_DIR : str = os.path.join(BASE_DOWNLOAD_DIR, "Music")
DEFAULT_VIDEO_DIR : str = os.path.join(BASE_DOWNLOAD_DIR, "Videos")

# ── Operational limits ────────────────────────────────────────────────────────

MIN_FREE_SPACE_MB        : int = 500
MAX_RETRIES              : int = 2
RETRY_DELAY_SECONDS      : int = 4
TITLE_FETCH_TIMEOUT_SEC  : int = 40
PROCESS_WAIT_TIMEOUT_SEC : int = 10    
FFMPEG_MERGE_TIMEOUT_SEC : int = 120
HISTORY_MAX_ITEMS        : int = 200

# ── Subprocess creation flags (platform-specific) ─────────────────────────────

_SUBPROCESS_FLAGS: Dict[str, Any] = {}

if IS_WINDOWS:
    _SUBPROCESS_FLAGS["creationflags"] = (
        subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    )

if IS_LINUX or IS_MAC:
    _SUBPROCESS_FLAGS["start_new_session"] = True


# ══════════════════════════════════════════════════════════════════════════════
#  §2-B  AUTO-UPDATE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

ENABLE_AUTO_UPDATE : bool = True

UPDATE_VERSION_URL = "https://raw.githubusercontent.com/BittarMO/Universal-Downloader/master/version.json"
APP_VERSION : str = "1.0.0"

UPDATE_CHECK_DELAY_SEC : int = 5

UPDATE_CHECK_TIMEOUT_SEC : int = 10


# ══════════════════════════════════════════════════════════════════════════════
#  §3  DESIGN TOKENS  —  single source of truth for every visual value
# ══════════════════════════════════════════════════════════════════════════════

class T:
    """
    Master design-token table.
    Edit values here; changes propagate everywhere automatically.
    """

    # ── §3.1  Main Window ─────────────────────────────────────────────────────
    class Window:
        W_PCT     : float = 0.44
        H_PCT     : float = 0.76
        MIN_W     : int   = 740
        MIN_H     : int   = 820
        MAX_W_PCT : float = 0.92
        MAX_H_PCT : float = 0.96
        RESIZABLE : bool  = True

    # ── §3.2  Scaling (responsive sizing) ────────────────────────────────────
    class Scale:
        REF_W : int   = 1920
        REF_H : int   = 1080
        MIN   : float = 0.52
        MAX   : float = 1.80
        MAIN  : float = 0.95

    # ── §3.3  Fonts (reference sizes at 1920×1080) ────────────────────────────
    class Font:
        APP_TITLE     : int = 28
        APP_SUB       : int = 13
        ICON_MAIN     : int = 30
        ICON_BTN      : int = 15
        MINI_BTN_ICON : int = 25
        STEP_NUM      : int = 15
        STEP_LABEL    : int = 15
        MODE_BTN      : int = 15
        URL_INPUT     : int = 14
        ADD_BTN       : int = 15
        BTN_SEC       : int = 12
        ROW_TITLE     : int = 14
        ROW_INFO      : int = 12
        ROW_BADGE     : int = 11
        PATH_LABEL    : int = 14
        START_BTN     : int = 15
        EMPTY_LABEL   : int = 13

        DLG_HEADER    : int = 16
        DLG_TITLE     : int = 15
        DLG_MSG       : int = 13
        DLG_ICON      : int = 18
        DLG_BTN       : int = 13

        ABOUT_MSG     : int = 15
        ABOUT_ICON    : int = 22
        ABOUT_TITLE   : int = 14
        ABOUT_MAX     : int = 14

        DONATE_LBL    : int = 18
        DONATE_BTN    : int = 18

        HIST_TITLE    : int = 12
        HIST_META     : int = 11
        HIST_ICON     : int = 25

        TOOL_HDR      : int = 15
        TOOL_MSG      : int = 12

        UPDATE_TITLE  : int = 14
        UPDATE_MSG    : int = 12
        UPDATE_BTN    : int = 13

    # ── §3.4  Sizes (reference dimensions at 1920×1080) ──────────────────────
    class Size:
        BTN_PRIMARY_H : int = 44
        BTN_SEC_H     : int = 36
        BTN_R_LG      : int = 10
        BTN_R_SM      : int = 8

        ICON_BOX      : int = 60
        ICON_BOX_R    : int = 10
        MINI_BTN_W    : int = 50
        MINI_BTN_H    : int = 60
        MINI_BTN_R    : int = 10

        INPUT_ROW_H   : int = 50
        INPUT_H       : int = 45
        INPUT_R       : int = 10
        LINK_ICON_W   : int = 38
        CLR_BTN       : int = 30
        CLR_BTN_R     : int = 8
        ADD_BTN_W     : int = 68
        ADD_BTN_H     : int = 44
        ADD_BTN_R     : int = 10

        MODE_BTN_H    : int = 46
        MODE_BTN_R    : int = 10

        STEP_CIR      : int = 30
        STEP_CIR_R    : int = 12

        QUEUE_ROW_R   : int = 10
        ROW_BADGE_W   : int = 50
        ROW_BADGE_H   : int = 26
        ROW_BADGE_R   : int = 6
        ROW_REM_W     : int = 28
        ROW_REM_H     : int = 28
        ROW_REM_R     : int = 8

        CLEAR_DONE_W  : int = 100
        CLEAR_DONE_H  : int = 34
        CLEAR_DONE_R  : int = 8
        START_BTN_H   : int = 48
        START_BTN_R   : int = 10
        PATH_BTN      : int = 38
        PATH_BTN_R    : int = 8

        DLG_OK_W      : int = 80
        DLG_OK_H      : int = 30
        DLG_OK_R      : int = 10
        DLG_FOLDER_W  : int = 100
        DLG_FOLDER_H  : int = 30
        DLG_FOLDER_R  : int = 10
        DLG_ICON_SZ   : int = 46
        DLG_ICON_R    : int = 14

        ABOUT_OK_W    : int = 60
        ABOUT_OK_H    : int = 30
        ABOUT_ICON_W  : int = 46
        ABOUT_ICON_H  : int = 46
        ABOUT_ICON_R  : int = 10

        PROG_BAR_H    : int = 6
        PROG_BAR_R    : int = 3

        HIST_ICON     : int = 50
        HIST_ICON_R   : int = 10
        HIST_PIN      : int = 40
        HIST_PIN_R    : int = 8
        HIST_ROW_R    : int = 10

        DONATE_BTN_W  : int = 80
        DONATE_BTN_H  : int = 40
        DONATE_BTN_R  : int = 10

        CARD_R        : int = 10
        PANEL_R       : int = 10
        QUEUE_R       : int = 10
        ACCENT_H      : int = 3
        SEP_H         : int = 1

        UPDATE_BAR_H  : int = 5
        UPDATE_BAR_R  : int = 3

    # ── §3.5  Spacing ─────────────────────────────────────────────────────────
    class Space:
        WIN_PX        : int = 28
        WIN_PY        : int = 24
        SECTION_GAP   : int = 10

        CARD_PX       : int = 18
        CARD_PY       : int = 14
        CARD_ROW_PY   : int = 13

        HDR_PY        : int = 10
        HDR_ICON_R    : int = 10
        HDR_BTN_GAP   : int = 8

        URL_PY        : int = 13
        URL_ICON_PX   : int = 12
        URL_ENTRY_PX  : int = 8
        URL_ENTRY_R   : int = 10
        ADD_BTN_PX    : int = 8
        ADD_BTN_PY    : int = 13

        MODE_GAP      : int = 8

        STEP_CIR_R    : int = 8
        STEP_PY       : int = 8

        QUEUE_HDR_PX  : int = 16
        QUEUE_HDR_PY  : int = 14
        QUEUE_PX      : int = 12
        QUEUE_PY_B    : int = 16
        QUEUE_ROW_PY  : int = 6
        QUEUE_EMPTY   : int = 28
        QUEUE_SPACER  : int = 8

        ROW_PX        : int = 14
        ROW_PY        : int = 9
        ROW_R_PX      : int = 10
        ROW_BADGE_PX  : int = 8

        PATH_PY       : int = 8

        DLG_SHELL_P   : int = 10
        DLG_BODY_PX   : int = 24
        DLG_BODY_PY   : int = 10
        DLG_BTN_PX    : int = 24
        DLG_BTN_PY_T  : int = 8
        DLG_BTN_PY_B  : int = 18
        DLG_ICON_R    : int = 10
        DLG_MSG_PY    : int = 4

        DONATE_PY     : int = 8

        ABOUT_BODY_PX  : int = 20
        ABOUT_BODY_PY  : int = 12
        ABOUT_HDR_GAP  : int = 12
        ABOUT_SEC_GAP  : int = 10
        ABOUT_LINE_PY  : int = 3
        ABOUT_SCROLL_P : int = 12
        ABOUT_FOOTER_P : int = 16

        HIST_SHELL_P  : int = 10
        HIST_BODY_PX  : int = 16
        HIST_BODY_PY  : int = 2
        HIST_BTN_PX   : int = 16
        HIST_BTN_PY   : int = 12
        HIST_ROW_PX   : int = 8
        HIST_ROW_PY   : int = 5
        HIST_ICON_PX  : int = 8
        HIST_ICON_R   : int = 10

        TOOL_PX       : int = 24
        TOOL_PY       : int = 16
        TOOL_HDR_PY   : int = 8
        TOOL_BAR_PY   : int = 12

        UPDATE_PX     : int = 18
        UPDATE_PY     : int = 10
        UPDATE_BAR_PY : int = 6

    # ── §3.6  Colors ──────────────────────────────────────────────────────────
    class Color:
        BG_ROOT      = "#0e0f12"
        BG_CARD      = "#161820"
        BG_INPUT     = "#0b0c0f"
        BG_ROW       = "#1d1f28"
        BG_HIST_ROW  = "#1d1f28"

        BORDER       = "#2a2d38"
        BORDER_STEP  = "#363a48"
        SEP          = "#222430"

        TEXT_BRIGHT  = "#edeef2"
        TEXT_MID     = "#a8aab8"
        TEXT_DIM     = "#6b6e80"
        TEXT_ERROR   = "#fb7185"

        MP3_MAIN     = "#0d9488"
        MP3_HOVER    = "#0f9d8f"
        MP3_ACTIVE   = "#2dd4bf"
        MP3_DIM      = "#042f2e"

        MP4_MAIN     = "#0B4661"
        MP4_HOVER    = "#0B4A68"
        MP4_ACTIVE   = "#286E8F"
        MP4_DIM      = "#0A212C"

        MODE_OFF     = "#1a1c26"
        MODE_OFF_HV  = "#23263a"

        BTN_SUBTLE    = "#1a1c26"
        BTN_SUBTLE_HV = "#252836"
        BTN_DANGER    = "#f43f5e"
        BTN_WARN      = "#f59e0b"

        HIST_MAIN    = "#3c2805"
        HIST_HOVER   = "#4D3102"

        UPDATE_MAIN  = "#1e3a5f"
        UPDATE_HOVER = "#1a3455"
        UPDATE_ACCENT= "#3b82f6"
        UPDATE_DIM   = "#0f1e33"

        DLG_INFO        = ("#edeef2", "i",  "#0b0c0f", "#2a2d38")
        DLG_WARNING     = ("#996408", "!",  "#1c1408", "#553704")
        DLG_ERROR       = ("#f43f5e", "✕",  "#1c0a10", "#881337")
        DLG_SUCCESS_MP3 = ("#2dd4bf", "✓",  "#021515", "#2dd4bf")
        DLG_SUCCESS_MP4 = ("#0B4661", "✓",  "#0A212C", "#0B4661")
        DLG_ABOUT       = DLG_INFO

    # ── §3.7  Dialog Geometry Constraints ────────────────────────────────────
    class Dialog:
        W_MIN_PCT    : float = 0.28
        W_MAX_PCT    : float = 0.68
        W_ABS_MIN    : int   = 500
        H_MIN_PCT    : float = 0.18
        H_MAX_PCT    : float = 0.55
        H_ABS_MIN    : int   = 220
        H_FOLDER_MIN : int   = 288

        HIST_W_MIN_PCT : float = 0.30
        HIST_W_MAX_PCT : float = 0.58
        HIST_W_ABS_MIN : int   = 400
        HIST_H_MIN_PCT : float = 0.36
        HIST_H_MAX_PCT : float = 0.86
        HIST_H_ABS_MIN : int   = 600

        TOOL_W_MIN_PCT : float = 0.22
        TOOL_W_MAX_PCT : float = 0.46
        TOOL_W_ABS_MIN : int   = 400
        TOOL_H_MIN_PCT : float = 0.16
        TOOL_H_MAX_PCT : float = 0.26
        TOOL_H_ABS_MIN : int   = 208

        ABOUT_W_PCT     : float = 0.72
        ABOUT_W_MIN_PCT : float = 0.48
        ABOUT_W_MAX_PCT : float = 0.88
        ABOUT_W_ABS_MIN : int   = 480
        ABOUT_W_ABS_MAX : int   = 700

        ABOUT_H_PCT     : float = 0.65
        ABOUT_H_MIN_PCT : float = 0.48
        ABOUT_H_MAX_PCT : float = 0.88
        ABOUT_H_ABS_MIN : int   = 480
        ABOUT_H_ABS_MAX : int   = 750

        ABOUT_REF_W     : int   = 520
        ABOUT_REF_H     : int   = 480
        ABOUT_SCALE_MIN : float = 0.90
        ABOUT_SCALE_MAX : float = 1.10

        UPDATE_W_MIN_PCT : float = 0.24
        UPDATE_W_MAX_PCT : float = 0.50
        UPDATE_W_ABS_MIN : int   = 420
        UPDATE_H_MIN_PCT : float = 0.14
        UPDATE_H_MAX_PCT : float = 0.22
        UPDATE_H_ABS_MIN : int   = 180

    # ── §3.8  Animation & Timing ──────────────────────────────────────────────
    class Anim:
        ADD_FRAMES      : tuple = ("●", "●●", "●●●", "●●")
        ADD_INTERVAL_MS : int   = 280
        FADE_IN_MS      : int   = 160
        TOOL_CLOSE_MS   : int   = 1100
        BTN_TICK_MS     : int   = 400


# ══════════════════════════════════════════════════════════════════════════════
#  §4  DATA MODELS
# ══════════════════════════════════════════════════════════════════════════════

class TaskStatus(str, Enum):
    PENDING     = "pending"
    FETCHING    = "fetching"
    DOWNLOADING = "downloading"
    DONE        = "done"
    FAILED      = "failed"
    CANCELLED   = "cancelled"
    RETRYING    = "retrying"


FINISHED_STATUSES : frozenset = frozenset({
    TaskStatus.DONE,
    TaskStatus.FAILED,
    TaskStatus.CANCELLED,
})

ACTIVE_STATUSES : frozenset = frozenset({
    TaskStatus.FETCHING,
    TaskStatus.DOWNLOADING,
    TaskStatus.RETRYING,
})


@dataclass
class DownloadTask:
    url           : str
    mode          : str
    status        : TaskStatus = TaskStatus.PENDING
    title         : str        = ""
    duration      : str        = ""
    filesize      : int        = 0
    filesize_str  : str        = ""
    error         : str        = ""
    retries       : int        = 0
    save_path     : str        = ""
    speed         : str        = ""
    eta           : str        = ""
    percent       : float      = 0.0
    added_at      : str        = field(default_factory=lambda: time.strftime("%H:%M:%S"))
    playlist_name : str        = ""
    _output_path  : str        = field(default="", repr=False)


class ModeStyle(NamedTuple):
    label  : str
    accent : str
    hover  : str
    active : str


MODE_STYLES: Dict[str, ModeStyle] = {
    "MP3": ModeStyle(
        label  = "♪  MP3  ·  320 Kbps",
        accent = T.Color.MP3_MAIN,
        hover  = T.Color.MP3_HOVER,
        active = T.Color.MP3_ACTIVE,
    ),
    "MP4": ModeStyle(
        label  = "🎬  MP4  ·  Best quality",
        accent = T.Color.MP4_MAIN,
        hover  = T.Color.MP4_HOVER,
        active = T.Color.MP4_ACTIVE,
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
#  §5  UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

_URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,}"
    r"(?:[/?#]\S*)?$",
    re.IGNORECASE,
)

_SUPPORTED_DOMAINS: Tuple[str, ...] = (
    "youtube.com", "youtu.be", "music.youtube.com", "m.youtube.com",
    "soundcloud.com",
    "vimeo.com", "dailymotion.com", "rumble.com", "bilibili.com",
    "twitch.tv", "m.twitch.tv", "clips.twitch.tv", "go.twitch.tv",
    "twitter.com", "x.com",
    "reddit.com", "v.redd.it",
    "facebook.com", "fb.watch",
    "instagram.com",
    "tiktok.com", "vm.tiktok.com",
)

_NET_KEYWORDS: Tuple[str, ...] = (
    "urlopen error", "connection refused", "network is unreachable",
    "failed to connect", "timed out", "timeout",
    "errno 11001", "errno -2",
    "nodename nor servname", "temporary failure in name resolution",
)

_RETRYABLE_KEYWORDS: Tuple[str, ...] = _NET_KEYWORDS + ("http error 429", "ssl")


def validate_url(url: str) -> Tuple[bool, str]:
    if not _URL_PATTERN.match(url):
        return False, "Invalid URL format. Must start with http:// or https://"

    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if host not in _SUPPORTED_DOMAINS:
        return False, (
            "Site not supported. Supported: YouTube, SoundCloud, Vimeo, "
            "Dailymotion, Twitch, Twitter/X, Reddit, Facebook, Instagram, TikTok…"
        )

    return True, ""


def format_filesize(byte_count: int) -> str:
    if byte_count <= 0:
        return "Unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    size  = float(byte_count)
    for i, unit in enumerate(units):
        if size < 1024.0 or i == len(units) - 1:
            return f"{size:.1f} {unit}" if i >= 2 else f"{int(size)} {unit}"
        size /= 1024.0


def classify_download_error(raw: str) -> str:
    lo = raw.lower()

    if any(kw in lo for kw in _NET_KEYWORDS):
        return "Network error – check your internet connection and try again."
    if "file already exists" in lo or "already exists" in lo:
        return "File already exists in save folder. Delete or change the folder."
    if any(kw in lo for kw in ("video unavailable", "private video",
                                "has been removed", "not available", "does not exist")):
        return "Video unavailable – private, removed, or geo-restricted."
    if "sign in" in lo or ("age" in lo and "restrict" in lo):
        return "Age-restricted video – requires login (not supported)."
    if "copyright" in lo or "blocked" in lo:
        return "Video blocked in your region due to copyright."
    if "playlist" in lo and "empty" in lo:
        return "Playlist is empty or all videos unavailable."
    if "requested format" in lo or ("format" in lo and "not available" in lo):
        return "Requested format not available for this video."
    if "http error 403" in lo:
        return "Access denied (HTTP 403) – may require login."
    if "http error 429" in lo:
        return "Rate-limited (HTTP 429) – wait a few minutes and retry."
    if "http error 404" in lo:
        return "Video not found (HTTP 404) – broken link."

    stripped = raw.strip()
    if stripped:
        last = stripped.splitlines()[-1]
        return last[:200] if last else "Unknown error."

    return "Unknown error during download."


def is_retryable_error(output: str) -> bool:
    return any(kw in output.lower() for kw in _RETRYABLE_KEYWORDS)


def terminate_process(proc: Optional[subprocess.Popen]) -> None:
    if proc is None:
        return

    for stream in (proc.stdout, proc.stderr):
        if stream:
            try:
                stream.close()
            except Exception:
                pass

    if IS_WINDOWS:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    elif IS_LINUX or IS_MAC:
        try:
            os.killpg(os.getpgid(proc.pid), _signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass
    else:
        try:
            proc.terminate()
        except Exception:
            pass

    deadline = time.time() + 1.5
    while time.time() < deadline and proc.poll() is None:
        time.sleep(0.02)

    if proc.poll() is None:
        try:
            if IS_LINUX or IS_MAC:
                os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
            else:
                proc.kill()
        except Exception:
            pass


def check_disk_space(path: str, min_mb: int) -> bool:
    try:
        target = path
        while target and not os.path.exists(target):
            target = os.path.dirname(target)
        target = target or os.path.expanduser("~")
        return shutil.disk_usage(target).free >= min_mb * 1024 * 1024
    except OSError as exc:
        log.warning("check_disk_space: %s", exc)
        return False


def open_in_explorer(path: str, create: bool = False) -> None:
    if not path:
        return
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    if create:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(folder):
        return

    if IS_WINDOWS:
        os.startfile(folder)
    elif IS_LINUX:
        subprocess.Popen(["xdg-open", folder])
    elif IS_MAC:
        subprocess.Popen(["open", folder])


def get_logical_screen(widget) -> Tuple[int, int]:
    try:
        scaling = ctk.ScalingTracker.get_window_dpi_scaling(widget)
        scaling = scaling if scaling > 0 else 1.0
    except AttributeError:
        try:
            scaling = float(widget.tk.call("tk", "scaling"))
            if scaling <= 0:
                scaling = 1.0
        except Exception:
            scaling = 1.0
    except Exception:
        scaling = 1.0

    return (
        int(widget.winfo_screenwidth()  / scaling),
        int(widget.winfo_screenheight() / scaling),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  §6  RESPONSIVE SCALING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class UIScale:
    factor: float = 1.0

    @classmethod
    def init(cls, widget) -> None:
        sw, sh     = get_logical_screen(widget)
        raw        = min(sw / T.Scale.REF_W, sh / T.Scale.REF_H)
        cls.factor = max(T.Scale.MIN, min(raw, T.Scale.MAX))

    @classmethod
    def f(cls, n: int) -> int:
        return max(8, round(n * cls.factor))

    @classmethod
    def s(cls, n: int) -> int:
        return max(1, round(n * cls.factor))

    @classmethod
    def p(cls, n: int) -> int:
        return max(0, round(n * cls.factor))

    @classmethod
    def fm(cls, n: int) -> int:
        return max(8, round(n * cls.factor * T.Scale.MAIN))

    @classmethod
    def sm(cls, n: int) -> int:
        return max(1, round(n * cls.factor * T.Scale.MAIN))

    @classmethod
    def pm(cls, n: int) -> int:
        return max(0, round(n * cls.factor * T.Scale.MAIN))

    @classmethod
    def clamp(cls, value: int, min_px: int, max_px: int) -> int:
        return max(min_px, min(max_px, value))

    @classmethod
    def f_clamped(cls, n: int, min_px: int = 10, max_px: int = 32) -> int:
        return cls.clamp(cls.f(n), min_px, max_px)

    @classmethod
    def s_clamped(cls, n: int, min_px: int = 4, max_px: int = 200) -> int:
        return cls.clamp(cls.s(n), min_px, max_px)

    @classmethod
    def p_clamped(cls, n: int, min_px: int = 0, max_px: int = 64) -> int:
        return cls.clamp(cls.p(n), min_px, max_px)


# ══════════════════════════════════════════════════════════════════════════════
#  §7  TOOL MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class ToolManager:
    def __init__(self, base_dir: str) -> None:
        self._base  = base_dir
        self._lock  = threading.Lock()
        self.yt_dlp = self._resolve(YT_DLP_BINARY)
        self.ffmpeg = self._resolve(FFMPEG_BINARY)

    def set_ffmpeg(self, path: str) -> None:
        with self._lock:
            self.ffmpeg = path

    def set_yt_dlp(self, path: str) -> None:
        with self._lock:
            self.yt_dlp = path

    def refresh(self) -> None:
        self.yt_dlp = self._resolve(YT_DLP_BINARY)
        self.ffmpeg = self._resolve(FFMPEG_BINARY)

    @property
    def missing(self) -> List[str]:
        result = []
        if not os.path.isfile(self.yt_dlp):
            result.append(YT_DLP_BINARY)
        if not os.path.isfile(self.ffmpeg):
            result.append(FFMPEG_BINARY)
        return result

    @property
    def ffmpeg_dir(self) -> str:
        return os.path.dirname(self.ffmpeg) if os.path.isfile(self.ffmpeg) else self._base

    def _resolve(self, name: str) -> str:
        if not IS_WINDOWS and name.endswith(".exe"):
            bare_name  = name[:-4]
            local_bare = os.path.join(self._base, bare_name)
            if os.path.isfile(local_bare):
                return local_bare
            system = shutil.which(bare_name)
            if system:
                return system
            return local_bare

        local = os.path.join(self._base, name)
        if os.path.isfile(local):
            return local

        system = shutil.which(name)
        if system:
            return system

        return local


# ══════════════════════════════════════════════════════════════════════════════
#  §8  TOOL DOWNLOADER DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ToolDownloader(ctk.CTkToplevel):
    _YT_DLP_URL: Dict[bool, str] = {
        True:  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        False: "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp",
    }
    _FFMPEG_URL: Dict[str, str] = {
        "win":   "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
                 "ffmpeg-master-latest-win64-gpl.zip",
        "linux": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
                 "ffmpeg-master-latest-linux64-gpl.tar.xz",
        "mac":   "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
                 "ffmpeg-master-latest-macos64-gpl.zip",
    }

    def __init__(
        self,
        master        : ctk.CTk,
        missing_tools : List[str],
        tools         : ToolManager,
    ) -> None:
        super().__init__(master)
        self.attributes("-alpha", 0)
        self.title("Downloading required tools…")
        if IS_WINDOWS and os.path.isfile(ICON_PATH):
            self.after(200, lambda: self.iconbitmap(ICON_PATH))
        self.resizable(False, False)
        self.configure(fg_color=T.Color.BG_ROOT)
        self.grab_set()

        self._missing           = missing_tools
        self._manager           = tools
        self.download_succeeded = False
        self.error_message      = ""
        self._ready_event       = threading.Event()

        self._center(master)
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._clear_and_close)
        self.attributes("-alpha", 1)
        threading.Thread(target=self._download_all, daemon=True).start()

    def _center(self, master: ctk.CTk) -> None:
        self.update_idletasks()
        sw, sh = get_logical_screen(self)
        w = min(max(360, int(sw * 0.22)), 500)
        h = min(max(140, int(sh * 0.12)), 180)
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()  - w) // 2
        y = master.winfo_y() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self) -> None:
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self._status_var = tk.StringVar(value="Preparing…")
        ctk.CTkLabel(
            main_frame,
            textvariable = self._status_var,
            font         = ("Segoe UI", UIScale.f(T.Font.TOOL_MSG)),
            text_color   = T.Color.TEXT_BRIGHT,
            anchor       = "center",
        ).pack(fill="x", pady=(0, 15))

        self._progress_var = tk.DoubleVar(value=0.0)
        ctk.CTkProgressBar(
            main_frame,
            variable      = self._progress_var,
            height        = UIScale.s(8),
            corner_radius = UIScale.s(4),
            fg_color      = T.Color.BORDER,
            progress_color= T.Color.MP3_ACTIVE,
        ).pack(fill="x", pady=(0, 25))

        self._exit_btn = ctk.CTkButton(
            main_frame,
            text          = "Exit",
            width         = UIScale.s(60),
            height        = UIScale.s(28),
            corner_radius = UIScale.s(8),
            fg_color      = T.Color.BTN_SUBTLE,
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = T.Color.TEXT_MID,
            font          = ("Segoe UI", UIScale.f(T.Font.DLG_BTN)),
            command       = self._clear_and_close,
        )
        self._exit_btn.pack(pady=(0, 0))

    def _clear_and_close(self) -> None:
        try:
            self.destroy()
        except Exception:
            pass

    def _set_status(self, text: str, progress: Optional[float] = None) -> None:
        self.after(0, lambda: self._status_var.set(text))
        if progress is not None:
            self.after(0, lambda: self._progress_var.set(progress))

    def _download_file(self, url: str, dest: str, label: str) -> None:
        CHUNK       = 65_536
        TIMEOUT_SEC = 30
        req = urllib.request.Request(url, headers={"User-Agent": "UniversalDownloader/2.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            total      = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest, "wb") as out:
                while chunk := resp.read(CHUNK):
                    out.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded / total
                        self._set_status(f"{label} ({int(pct * 100)}%)", pct)
                    else:
                        self._set_status(f"{label} ({downloaded // 1024} KB)")

    def _download_with_fallback(
        self,
        url           : str,
        dest          : str,
        label         : str,
        fallback_func : Optional[Callable] = None,
    ) -> bool:
        try:
            self._download_file(url, dest, label)
            return True
        except Exception as exc:
            log.warning("Primary download failed: %s", exc)
            if fallback_func:
                try:
                    alt = fallback_func(label)
                    if alt:
                        self._download_file(alt, dest, f"{label} (fallback)")
                        return True
                except Exception as exc2:
                    log.warning("Fallback also failed: %s", exc2)
        return False

    def _latest_yt_dlp_url(self, _label: str) -> Optional[str]:
        import json
        api = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        try:
            with urllib.request.urlopen(api, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            for asset in data.get("assets", []):
                name = asset["name"]
                if IS_WINDOWS and name.endswith(".exe"):
                    return asset["browser_download_url"]
                if not IS_WINDOWS and name == "yt-dlp" and "exe" not in name:
                    return asset["browser_download_url"]
        except Exception as exc:
            log.warning("_latest_yt_dlp_url: %s", exc)
        return None

    def _latest_ffmpeg_url(self, _label: str) -> Optional[str]:
        import json
        api         = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
        pattern_map = {
            "win":   "win64-gpl.zip",
            "linux": "linux64-gpl.tar.xz",
            "mac":   "macos64-gpl.zip",
        }
        key     = "win" if IS_WINDOWS else ("mac" if IS_MAC else "linux")
        pattern = pattern_map[key]
        try:
            with urllib.request.urlopen(api, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            for asset in data.get("assets", []):
                if asset["name"].endswith(pattern):
                    return asset["browser_download_url"]
        except Exception as exc:
            log.warning("_latest_ffmpeg_url: %s", exc)
        return None

    def _download_yt_dlp(self) -> None:
        dest    = os.path.join(BASE_DATA_DIR, YT_DLP_BINARY)
        success = self._download_with_fallback(
            self._YT_DLP_URL[IS_WINDOWS],
            dest,
            "yt-dlp",
            self._latest_yt_dlp_url,
        )
        if not success:
            raise RuntimeError(
                f"Could not download yt-dlp.\n"
                f"Download manually from https://github.com/yt-dlp/yt-dlp/releases\n"
                f"and place it here: {dest}"
            )
        if IS_LINUX or IS_MAC:
            os.chmod(dest, 0o755)

    def _download_ffmpeg_windows(self) -> None:
        zip_path = os.path.join(BASE_DATA_DIR, "_ffmpeg.zip")
        dest_exe = os.path.join(BASE_DATA_DIR, "ffmpeg.exe")
        success  = self._download_with_fallback(
            self._FFMPEG_URL["win"],
            zip_path,
            "ffmpeg (ZIP)",
            self._latest_ffmpeg_url,
        )
        if not success:
            raise RuntimeError(
                f"Could not download ffmpeg.\n"
                f"Download manually from https://github.com/BtbN/FFmpeg-Builds/releases\n"
                f"and place ffmpeg.exe here: {dest_exe}"
            )

        self._set_status("Extracting ffmpeg…", 0.95)
        found = False
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                parts = name.replace("\\", "/").split("/")
                if (
                    parts[-1].lower() == "ffmpeg.exe"
                    and "__macosx" not in name.lower()
                    and "ffprobe" not in name.lower()
                ):
                    with zf.open(name) as src, open(dest_exe, "wb") as out:
                        out.write(src.read())
                    found = True
                    break

        if not found:
            raise RuntimeError("ffmpeg.exe not found inside archive.")

        os.remove(zip_path)
        self._manager.set_ffmpeg(dest_exe)

    def _download_ffmpeg_unix(self) -> None:
        import tarfile

        key     = "mac" if IS_MAC else "linux"
        url     = self._FFMPEG_URL[key]
        is_tar  = url.endswith(".xz")
        ext     = ".tar.xz" if is_tar else ".zip"
        archive = os.path.join(BASE_DATA_DIR, f"_ffmpeg{ext}")
        dest    = os.path.join(BASE_DATA_DIR, FFMPEG_BINARY)

        success = self._download_with_fallback(
            url,
            archive,
            "ffmpeg (archive)",
            self._latest_ffmpeg_url,
        )
        if not success:
            raise RuntimeError(
                f"Could not download ffmpeg.\n"
                f"Download manually from https://github.com/BtbN/FFmpeg-Builds/releases\n"
                f"and place the 'ffmpeg' binary here: {dest}"
            )

        self._set_status("Extracting ffmpeg…", 0.95)
        found = False

        if is_tar:
            with tarfile.open(archive, "r:xz") as tar:
                for member in tar.getmembers():
                    parts = member.name.replace("\\", "/").split("/")
                    if (
                        parts[-1] == "ffmpeg"
                        and member.isfile()
                        and "ffprobe" not in member.name
                    ):
                        f = tar.extractfile(member)
                        if f:
                            with open(dest, "wb") as out:
                                out.write(f.read())
                            found = True
                        break
                    
        else:
            with zipfile.ZipFile(archive, "r") as zf:
                for name in zf.namelist():
                    parts = name.replace("\\", "/").split("/")
                    if (
                        parts[-1] == "ffmpeg"
                        and not name.endswith("/")
                        and "ffprobe" not in name
                        and "__macosx" not in name.lower()
                    ):
                        with zf.open(name) as src, open(dest, "wb") as out:
                            out.write(src.read())
                        found = True
                        break

        try:
            os.remove(archive)
        except OSError:
            pass

        if not found or not os.path.isfile(dest):
            raise RuntimeError(
                f"ffmpeg binary not found inside archive.\n"
                f"Download manually from https://github.com/BtbN/FFmpeg-Builds/releases\n"
                f"and place the 'ffmpeg' binary here: {dest}"
            )

        os.chmod(dest, 0o755)
        self._manager.set_ffmpeg(dest)

    def _download_all(self) -> None:
        self._ready_event.wait()

        try:
            os.makedirs(BASE_DATA_DIR, exist_ok=True)
            for tool in self._missing:
                if "yt-dlp" in tool:
                    self._download_yt_dlp()
                elif "ffmpeg" in tool:
                    if IS_WINDOWS:
                        self._download_ffmpeg_windows()
                    else:
                        self._download_ffmpeg_unix()

            self.download_succeeded = True
            self._set_status("Done!", 1.0)
            if self.winfo_exists():
                self.after(T.Anim.TOOL_CLOSE_MS, self._safe_destroy)

        except Exception as exc:
            log.error("ToolDownloader._download_all: %s", exc)
            self.error_message = str(exc)
            if self.winfo_exists():
                self.after(0, self._safe_destroy)

    def _safe_destroy(self) -> None:
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass

    def show(self) -> Tuple[bool, str]:
        self._ready_event.set()
        self.wait_window(self)
        return self.download_succeeded, self.error_message


# ══════════════════════════════════════════════════════════════════════════════
#  §9  DOWNLOAD HISTORY
# ══════════════════════════════════════════════════════════════════════════════

class DownloadHistory:
    def __init__(self) -> None:
        self._records : List[Dict[str, Any]] = []
        self._lock    : threading.Lock       = threading.Lock()

    def add(self, task: DownloadTask) -> None:
        entry = {
            "title"    : task.title or task.url,
            "url"      : task.url,
            "mode"     : task.mode,
            "status"   : task.status.value,
            "time"     : time.strftime("%Y-%m-%d %H:%M"),
            "save_path": task.save_path,
        }
        with self._lock:
            self._records.insert(0, entry)
            self._records = self._records[:HISTORY_MAX_ITEMS]
            print(f"[HISTORY] Added {task.title[:30]}, total records: {len(self._records)}")

    def clear(self) -> None:
        with self._lock:
            self._records.clear()

    @property
    def items(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._records)


# ══════════════════════════════════════════════════════════════════════════════
#  §10  QUEUE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class QueueManager:
    def __init__(self) -> None:
        self._tasks : List[DownloadTask] = []
        self._lock  = threading.Lock()

    def add_task(self, task: DownloadTask) -> None:
        with self._lock:
            self._tasks.insert(0, task)         

    def add_tasks(self, tasks: List[DownloadTask]) -> None:
        with self._lock:
            for task in reversed(tasks):             
                self._tasks.insert(0, task)

    def remove_task(self, task: DownloadTask) -> bool:
        with self._lock:
            if task in self._tasks:
                self._tasks.remove(task)
                return True
            return False

    def remove_finished(self) -> List[DownloadTask]:
        with self._lock:
            kept    = [t for t in self._tasks if t.status not in FINISHED_STATUSES]
            removed = [t for t in self._tasks if t.status in     FINISHED_STATUSES]
            self._tasks = kept
            return removed

    def next_pending(self) -> Optional[DownloadTask]:
        with self._lock:
            return next((t for t in self._tasks if t.status == TaskStatus.PENDING), None)

    def all_tasks(self) -> List[DownloadTask]:
        with self._lock:
            return list(self._tasks)

    def has_pending(self) -> bool:
        with self._lock:
            return any(t.status == TaskStatus.PENDING for t in self._tasks)

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._tasks)


# ══════════════════════════════════════════════════════════════════════════════
#  §10-A  AUTO-UPDATE SYSTEM
#
#  Controlled entirely by the ENABLE_AUTO_UPDATE flag defined in §2-B.
#  When the flag is False, AutoUpdater.start() returns immediately without
#  spawning any threads, touching any files, or displaying any UI.
# ══════════════════════════════════════════════════════════════════════════════

def _parse_version(v: str) -> Tuple[int, ...]:
    """Convert a SemVer string such as '1.2.3' to a comparable integer tuple."""
    try:
        return tuple(int(x) for x in re.split(r"[.\-]", v.strip()) if x.isdigit())
    except Exception:
        return (0,)


def _version_newer(remote: str, local: str) -> bool:
    """Return True when *remote* is strictly newer than *local*."""
    return _parse_version(remote) > _parse_version(local)


class UpdateBanner(ctk.CTkFrame):
    """
    Compact, non-modal banner injected at the bottom of the main window when an
    update is available.  It shows a progress bar during download and collapses
    itself on completion or dismissal.
    """

    def __init__(
        self,
        parent         : ctk.CTkFrame,
        version        : str,
        on_auto_update : Callable[[], None],
        on_dismiss     : Callable[[], None],
    ) -> None:
        super().__init__(
            parent,
            fg_color      = T.Color.UPDATE_MAIN,
            corner_radius = UIScale.s(8),
            border_width  = 1,
            border_color  = T.Color.UPDATE_ACCENT,
        )

        self._on_auto   = on_auto_update
        self._on_dismiss= on_dismiss
        self._progress  = tk.DoubleVar(value=0.0)
        self._status    = tk.StringVar(value="")
        self._version   = version
        self._in_progress = False

        self._build(version)

    def set_ready_reboot(self) -> None:
        """Windows‑specific: update requires a restart."""
        self._progress.set(1.0)
        self._status.set("The update will be applied when you restart the program.")
        self._install_btn.configure(state="disabled")
        self._manual_btn.configure(text="OK", command=self._dismiss)
    
    def _build(self, version: str) -> None:
        sp = T.Space

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(
            fill="x",
            padx=UIScale.p(sp.UPDATE_PX),
            pady=UIScale.p(sp.UPDATE_PY),
        )
        content.grid_columnconfigure(1, weight=1)

        # Left icon
        ctk.CTkLabel(
            content,
            text       = "🔄",
            font       = ("Segoe UI", UIScale.f(14)),
            text_color = T.Color.UPDATE_ACCENT,
        ).grid(row=0, column=0, rowspan=2, padx=(0, UIScale.p(8)), sticky="ns")

        # Title row
        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.grid(row=0, column=1, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_row,
            text       = f"Update available — v{version}",
            font       = ("Segoe UI", UIScale.f(T.Font.UPDATE_TITLE), "bold"),
            text_color = T.Color.TEXT_BRIGHT,
            anchor     = "w",
        ).grid(row=0, column=0, sticky="w")

        # Dismiss button (top-right)
        ctk.CTkButton(
            title_row,
            text          = "✕",
            width         = UIScale.s(22),
            height        = UIScale.s(22),
            corner_radius = UIScale.s(6),
            fg_color      = "transparent",
            hover_color   = T.Color.UPDATE_HOVER,
            text_color    = T.Color.TEXT_DIM,
            font          = ("Segoe UI", UIScale.f(10)),
            command       = self._dismiss,
        ).grid(row=0, column=1, sticky="e", padx=(UIScale.p(8), 0))

        # Status / sub-label row
        self._status_lbl = ctk.CTkLabel(
            content,
            textvariable = self._status,
            font         = ("Segoe UI", UIScale.f(T.Font.UPDATE_MSG)),
            text_color   = T.Color.TEXT_DIM,
            anchor       = "w",
        )
        self._status_lbl.grid(row=1, column=1, sticky="ew")
        self._status.set("Downloading in the background…")

        # Progress bar (hidden until download starts)
        self._bar = ctk.CTkProgressBar(
            content,
            variable       = self._progress,
            height         = UIScale.s(T.Size.UPDATE_BAR_H),
            corner_radius  = UIScale.s(T.Size.UPDATE_BAR_R),
            fg_color       = T.Color.UPDATE_DIM,
            progress_color = T.Color.UPDATE_ACCENT,
        )
        self._bar.grid(
            row=2, column=0, columnspan=3, sticky="ew",
            pady=(UIScale.p(sp.UPDATE_BAR_PY), 0),
        )

        # Action buttons
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=3, sticky="e",
                     pady=(UIScale.p(6), 0))

        self._install_btn = ctk.CTkButton(
            btn_row,
            text          = "Install & Restart",
            height        = UIScale.s(28),
            width         = UIScale.s(120),
            corner_radius = UIScale.s(8),
            fg_color      = T.Color.UPDATE_ACCENT,
            hover_color   = "#2563eb",
            text_color    = "#ffffff",
            font          = ("Segoe UI", UIScale.f(T.Font.UPDATE_BTN), "bold"),
            state         = "disabled",
            command       = self._install,
        )
        self._install_btn.pack(side="right")

        self._manual_btn = ctk.CTkButton(
            btn_row,
            text          = "Later",
            height        = UIScale.s(28),
            width         = UIScale.s(72),
            corner_radius = UIScale.s(8),
            fg_color      = T.Color.UPDATE_DIM,
            hover_color   = T.Color.UPDATE_HOVER,
            text_color    = T.Color.TEXT_MID,
            font          = ("Segoe UI", UIScale.f(T.Font.UPDATE_BTN)),
            command       = self._dismiss,
        )
        self._manual_btn.pack(side="right", padx=(0, UIScale.p(8)))

    # ── Public API ────────────────────────────────────────────────────────────

    def set_progress(self, pct: float, status_text: str = "") -> None:
        """Update the progress bar and optional status text (0–100)."""
        self._progress.set(min(1.0, pct / 100.0))
        if status_text:
            self._status.set(status_text)

    def set_ready(self) -> None:
        """Signal that the download is complete and ready to install."""
        self._progress.set(1.0)
        self._status.set("Download complete — ready to install.")
        self._install_btn.configure(state="normal")
        self._manual_btn.configure(text="Later")

    def set_error(self, msg: str) -> None:
        """Signal a download error."""
        self._status.set(f"Update failed: {msg[:60]}")
        self._install_btn.configure(state="disabled")
        self._manual_btn.configure(text="Dismiss")

    def _install(self) -> None:
        self._on_auto()

    def _dismiss(self) -> None:
        self._on_dismiss()
        try:
            self.destroy()
        except Exception:
            pass


class AutoUpdater:
    """
    Self-contained auto-update engine.

    Lifecycle
    ---------
    1. start()              — schedule the version check after UPDATE_CHECK_DELAY_SEC
    2. _check_version()     — background: fetch version.json, compare versions
    3. _notify_available()  — main thread: inject UpdateBanner into the window
    4. _download_update()   — background: stream the new binary to a temp file
                              with resume support (Range header)
    5. install_and_restart()— main thread: replace binary, re-launch process

    Disabling
    ---------
    If ENABLE_AUTO_UPDATE is False the start() method returns immediately and
    nothing else in this class ever executes.
    """

    _TEMP_SUFFIX     : str = ".update_part"
    _CHUNK_SIZE      : int = 65_536
    _CONNECT_TIMEOUT : int = UPDATE_CHECK_TIMEOUT_SEC
    _DOWNLOAD_TIMEOUT: int = 30

    def __init__(self, root: ctk.CTk, main_frame: ctk.CTkFrame) -> None:
        self._root        = root
        self._main_frame  = main_frame
        self._banner      : Optional[UpdateBanner]   = None
        self._new_path    : str                      = ""
        self._remote_info : Dict[str, str]           = {}
        self._stop        : threading.Event          = threading.Event()

    # ── Entry point ───────────────────────────────────────────────────────────

    def start(self) -> None:
        """Schedule the first version check. No-op when updates are disabled."""
        if not ENABLE_AUTO_UPDATE:
            return
        self._root.after(UPDATE_CHECK_DELAY_SEC * 1000, self._begin_check)

    # ── Step 1: version check ─────────────────────────────────────────────────

    def _begin_check(self) -> None:
        """Fire the version-check on a daemon thread."""
        threading.Thread(target=self._check_version, daemon=True).start()

    def _check_version(self) -> None:
        """Background: fetch the remote version manifest and compare."""
        import json

        try:
            req = urllib.request.Request(
                UPDATE_VERSION_URL,
                headers={"User-Agent": "UniversalDownloader-Updater/1.0",
                         "Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(req, timeout=self._CONNECT_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)

            remote_ver = str(data.get("version", "")).strip()
            remote_url = str(data.get("url", "")).strip()
            checksum   = str(data.get("checksum_sha256", "")).strip()

            if not remote_ver or not remote_url:
                log.debug("AutoUpdater: version manifest missing fields.")
                return

            if not _version_newer(remote_ver, APP_VERSION):
                log.debug("AutoUpdater: already up to date (%s).", APP_VERSION)
                return

            self._remote_info = {
                "version" : remote_ver,
                "url"     : remote_url,
                "checksum": checksum,
            }
            self._root.after(0, self._notify_available, remote_ver)

        except Exception as exc:
            log.debug("AutoUpdater._check_version: %s", exc)

    # ── Step 2: notify UI and begin background download ───────────────────────

    def _notify_available(self, version: str) -> None:
        """Main thread: inject the update banner and start the background download."""
        if self._banner is not None:
            return

        self._banner = UpdateBanner(
            parent         = self._main_frame,
            version        = version,
            on_auto_update = self.install_and_restart,
            on_dismiss     = self._on_banner_dismissed,
        )
        self._banner.grid(
            row=7, column=0, sticky="ew",
            pady=(UIScale.p(T.Space.SECTION_GAP), 0),
        )

        threading.Thread(
            target=self._download_update,
            args=(self._remote_info["url"],),
            daemon=True,
        ).start()

    def _on_banner_dismissed(self) -> None:
        """User clicked 'Later' or '✕' — stop the download and forget the banner."""
        self._stop.set()
        self._banner = None

    # ── Step 3: background download with resume ───────────────────────────────

    def _download_update(self, url: str) -> None:
        """
        Stream the update binary to a temp file.
        Sends a Range header if a partial file already exists (resume support).
        """
        import hashlib

        if IS_FROZEN:
            dest_dir = os.path.dirname(sys.executable)
        else:
            dest_dir = os.path.dirname(os.path.abspath(__file__))

        tmp_path = os.path.join(dest_dir, "_update" + self._TEMP_SUFFIX)

        existing_bytes = 0
        if os.path.isfile(tmp_path):
            existing_bytes = os.path.getsize(tmp_path)

        try:
            headers = {"User-Agent": "UniversalDownloader-Updater/1.0"}
            if existing_bytes > 0:
                headers["Range"] = f"bytes={existing_bytes}-"

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self._DOWNLOAD_TIMEOUT) as resp:
                status_code = resp.getcode()
                total_raw   = resp.headers.get("Content-Length", "0")
                chunk_total = int(total_raw) if total_raw.isdigit() else 0

                if status_code == 206:
                    total_bytes = existing_bytes + chunk_total
                    file_mode   = "ab"
                else:
                    total_bytes   = chunk_total
                    existing_bytes = 0
                    file_mode     = "wb"

                downloaded = existing_bytes
                hasher     = hashlib.sha256()

                with open(tmp_path, file_mode) as out:
                    if file_mode == "ab" and existing_bytes > 0:
                        with open(tmp_path, "rb") as existing_f:
                            for chunk in iter(lambda: existing_f.read(65536), b""):
                                hasher.update(chunk)

                    while not self._stop.is_set():
                        chunk = resp.read(self._CHUNK_SIZE)
                        if not chunk:
                            break
                        out.write(chunk)
                        hasher.update(chunk)
                        downloaded += len(chunk)

                        if total_bytes > 0:
                            pct  = downloaded / total_bytes * 100.0
                            text = (
                                f"Downloading update… "
                                f"{format_filesize(downloaded)} / "
                                f"{format_filesize(total_bytes)}"
                            )
                        else:
                            pct  = 0.0
                            text = f"Downloading update… {format_filesize(downloaded)}"

                        if self._banner is not None:
                            self._root.after(0, self._banner.set_progress, pct, text)

            if self._stop.is_set():
                return

            # Optional checksum verification
            expected = self._remote_info.get("checksum", "")
            if expected and hasher.hexdigest().lower() != expected.lower():
                raise ValueError("Checksum mismatch — update file may be corrupt.")

            self._new_path = tmp_path
            if self._banner is not None:
                self._root.after(0, self._banner.set_ready)

        except Exception as exc:
            log.error("AutoUpdater._download_update: %s", exc)
            if self._banner is not None:
                msg = str(exc)[:80]
                self._root.after(0, self._banner.set_error, msg)

    # ── Step 4: install & restart ─────────────────────────────────────────────

    def install_and_restart(self) -> None:

        if not self._new_path or not os.path.isfile(self._new_path):
            log.error("AutoUpdater.install_and_restart: no downloaded file found.")
            return

        try:
            if IS_FROZEN:
                current_exe = sys.executable
            else:
                current_exe = os.path.abspath(__file__)

            if IS_WINDOWS:
                self._install_windows(current_exe, self._new_path)
            else:
                self._install_unix(current_exe, self._new_path)

        except Exception as exc:
            log.error("AutoUpdater.install_and_restart: %s", exc)
            if self._banner is not None:
                self._root.after(0, self._banner.set_error, str(exc)[:80])

    def _install_windows(self, current_exe: str, new_file: str) -> None:

        import ctypes

        MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
        MOVEFILE_REPLACE_EXISTING   = 0x1

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

        ok = kernel32.MoveFileExW(
            new_file,
            current_exe,
            MOVEFILE_DELAY_UNTIL_REBOOT | MOVEFILE_REPLACE_EXISTING,
        )

        if not ok:
            error_code = kernel32.GetLastError()
            raise RuntimeError(
                f"MoveFileEx failed (error code: {error_code}).\n"
                f"Replace the file manually:\n"
                f"  New file : {new_file}\n"
                f"  Target   : {current_exe}"
            )

        if self._banner is not None:
            self._root.after(
                0,
                self._banner.set_ready_reboot, 
            )
        self._root.after(0, self._show_reboot_notice)

    def _show_reboot_notice(self) -> None:
        import tkinter.messagebox as mb
        mb.showinfo(
            "Update Ready",
            "The update will be applied when you restart the program.\n"
            "Please close the application and reopen it to complete the update.",
            parent=self._root,
        )

    def _install_unix(self, current_exe: str, new_file: str) -> None:
        """On Unix we can replace the file directly then re-exec."""
        import stat

        backup = current_exe + ".old"
        try:
            shutil.move(current_exe, backup)
            shutil.move(new_file, current_exe)
            st = os.stat(current_exe)
            os.chmod(current_exe, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            try:
                os.remove(backup)
            except OSError:
                pass
        except Exception:
            # Attempt rollback
            if os.path.isfile(backup) and not os.path.isfile(current_exe):
                shutil.move(backup, current_exe)
            raise

        args = [current_exe] + sys.argv[1:]
        self._root.after(0, self._root.destroy)
        self._root.after(200, lambda: os.execv(current_exe, args))


# ══════════════════════════════════════════════════════════════════════════════
#  §11  DOWNLOAD WORKER
# ══════════════════════════════════════════════════════════════════════════════

class DownloadWorker:
    _RE_PLAYLIST  = re.compile(r"\[download\]\s+Downloading item (\d+) of (\d+)")
    _RE_PERCENT   = re.compile(r"\[download\]\s+(\d+\.?\d*)%")
    _RE_SPEED_ETA = re.compile(
        r"\[download\]\s+\d+\.?\d*%.*?at\s+([\d.]+\s*\S+/s).*?ETA\s+(\d+:\d+(?::\d+)?|Unknown)",
        re.IGNORECASE,
    )

    _path_lock: threading.Lock = threading.Lock()

    def __init__(
        self,
        task              : DownloadTask,
        tools             : ToolManager,
        max_retries       : int,
        music_dir_func    : Callable[[], str],
        video_dir_func    : Callable[[], str],
        progress_callback : Callable[[DownloadTask, float, str, str], None],
        status_callback   : Callable[[DownloadTask, str], None],
        is_stopped        : Callable[[], bool],
    ) -> None:
        self.task            = task
        self.tools           = tools
        self._max_retries    = max_retries
        self._music_dir      = music_dir_func
        self._video_dir      = video_dir_func
        self._on_progress    = progress_callback
        self._on_status      = status_callback
        self.is_stopped      = is_stopped
        self._active_process : Optional[subprocess.Popen] = None
        self._playlist_total : int = 0
        self._playlist_done  : int = 0

    def run(self) -> Tuple[bool, str]:
        while True:
            if self.is_stopped():
                return False, "Cancelled by user."

            self.task.status = TaskStatus.FETCHING
            self._on_status(self.task, "Fetching video info…")
            if not self.task.title:
                self._fetch_metadata()

            if self.is_stopped():
                return False, "Cancelled by user."

            self.task.status    = TaskStatus.DOWNLOADING
            self.task.save_path = self._save_dir()
            self.task.percent   = 0.0
            self.task.speed     = ""
            self.task.eta       = ""

            with DownloadWorker._path_lock:
                self.task._output_path = self._unique_output_path()

            self._on_status(self.task, "Downloading…")
            success, raw_error, is_network = self._execute_download()

            if self.is_stopped():
                return False, "Cancelled by user."

            if success:
                self.task.status  = TaskStatus.DONE
                self.task.percent = 100.0
                self._on_status(self.task, f"Done · {self.task.mode}")
                return True, ""

            friendly = classify_download_error(raw_error)

            if is_network and self.task.retries < self._max_retries:
                self.task.retries += 1
                self.task.status   = TaskStatus.RETRYING
                self._on_status(
                    self.task,
                    f"Retry {self.task.retries}/{self._max_retries} in {RETRY_DELAY_SECONDS}s…",
                )
                for _ in range(RETRY_DELAY_SECONDS * 10):
                    if self.is_stopped():
                        return False, "Cancelled by user."
                    time.sleep(0.1)
                continue

            self.task.status = TaskStatus.FAILED
            self.task.error  = friendly
            self._on_status(self.task, f"Failed: {friendly[:60]}")
            return False, friendly

    def _save_dir(self) -> str:
        return self._music_dir() if self.task.mode == "MP3" else self._video_dir()

    def _unique_output_path(self) -> str:
        base_dir = self._save_dir()
        playlist = (self.task.playlist_name or "").strip()

        if playlist:
            clean_playlist = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", playlist).strip(". ")
            folder = os.path.join(base_dir, clean_playlist)
        else:
            folder = base_dir

        if os.path.exists(folder) and not os.path.isdir(folder):
            counter = 1
            while True:
                candidate = f"{folder} ({counter})"
                if not os.path.exists(candidate) or os.path.isdir(candidate):
                    folder = candidate
                    break
                counter += 1

        os.makedirs(folder, exist_ok=True)

        raw_title   = self.task.title or self.task.url
        clean_title = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", raw_title).strip(". _")
        clean_title = clean_title[:180] or "video"

        ext       = "mp3" if self.task.mode == "MP3" else "mp4"
        base_path = os.path.join(folder, f"{clean_title}.{ext}")

        if not os.path.exists(base_path):
            return base_path

        counter = 1
        while True:
            new_path = os.path.join(folder, f"{clean_title} ({counter}).{ext}")
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def _build_command(self) -> List[str]:
        if self.task.mode == "MP3":
            fmt_args = ["-x", "--audio-format", "mp3", "--audio-quality", "320K"]
        else:
            fmt_args = [
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "--merge-output-format", "mp4",
            ]

        out_path = self.task._output_path or self._unique_output_path()
        return [
            self.tools.yt_dlp, "--no-update",
            *fmt_args,
            "--ffmpeg-location", self.tools.ffmpeg_dir,
            "--newline", "--continue",
            "-o", out_path,
            self.task.url,
        ]

    def _fetch_metadata(self) -> None:
        cmd = [
            self.tools.yt_dlp, "--no-update", "--quiet",
            "--print", "title",
            "--print", "duration_string",
            "--print", "filesize_approx",
            "--playlist-items", "1",
            self.task.url,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output = True,
                text           = True,
                encoding       = "utf-8",
                errors         = "replace",
                timeout        = TITLE_FETCH_TIMEOUT_SEC,
                **_SUBPROCESS_FLAGS,
            )
            if result.returncode != 0:
                return
            lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
            self._apply_metadata(lines)
        except Exception as exc:
            log.debug("_fetch_metadata: %s", exc)

    def _apply_metadata(self, lines: List[str]) -> None:
        if len(lines) >= 1 and lines[0]:
            self.task.title = lines[0][:200]
        if len(lines) >= 2 and lines[1]:
            dur = lines[1].lstrip("0:")
            self.task.duration = dur or "0:00"
        if len(lines) >= 3:
            raw = lines[2].strip()
            if raw.isdigit():
                size = int(raw)
                if size > 0:
                    self.task.filesize     = size
                    self.task.filesize_str = format_filesize(size)

    def _execute_download(self) -> Tuple[bool, str, bool]:
        error_lines          = []
        self._playlist_total = 0
        self._playlist_done  = 0

        try:
            save_dir = self._save_dir()

            try:
                if os.path.exists(save_dir):
                    free_mb = shutil.disk_usage(save_dir).free / (1024 * 1024)
                else:
                    parent  = os.path.dirname(save_dir)
                    free_mb = shutil.disk_usage(parent).free / (1024 * 1024) if parent else 0

                if self.task.filesize and self.task.filesize > 0:
                    required_mb = max(MIN_FREE_SPACE_MB, int(self.task.filesize * 1.1 / (1024 * 1024)))
                else:
                    required_mb = MIN_FREE_SPACE_MB

                if free_mb < required_mb:
                    return (
                        False,
                        f"Not enough disk space. Need ~{required_mb} MB, "
                        f"only {int(free_mb)} MB available in:\n{save_dir}",
                        False,
    )
            except OSError as exc:
                log.warning("Could not check disk space: %s", exc)

            os.makedirs(save_dir, exist_ok=True)

            process = subprocess.Popen(
                self._build_command(),
                stdout   = subprocess.PIPE,
                stderr   = subprocess.STDOUT,
                text     = True,
                encoding = "utf-8",
                errors   = "replace",
                bufsize  = 1,
                **_SUBPROCESS_FLAGS,
            )
            self._active_process = process

            _error_keywords = (
                "error", "failed", "warning", "unable", "cannot",
                "http error", "timed out", "timeout", "refused",
                "unavailable", "blocked", "forbidden",
            )
            for raw_line in process.stdout:
                if self.is_stopped():
                    terminate_process(process)
                    return False, "Cancelled by user.", False

                line = raw_line.strip()
                if line and (
                    any(kw in line.lower() for kw in _error_keywords)
                    or line.startswith("ERROR:")
                    or line.startswith("[error]")
                ):
                    error_lines.append(line)

                self._parse_progress(line)

            try:
                process.wait(timeout=FFMPEG_MERGE_TIMEOUT_SEC)
            except subprocess.TimeoutExpired:
                terminate_process(process)
                return False, "Process timed out during merge.", True

            if self.is_stopped():
                return False, "Cancelled by user.", False

            if process.returncode != 0:
                raw_err = "\n".join(error_lines)
                return False, raw_err, is_retryable_error(raw_err)

            self._remove_part_files()
            return True, "", False

        except Exception as exc:
            log.error("_execute_download: %s", exc)
            return False, str(exc), False
        finally:
            self._active_process = None

    def _parse_progress(self, line: str) -> None:
        m = self._RE_PLAYLIST.search(line)
        if m:
            current = int(m.group(1))
            total   = int(m.group(2))
            if total > 0:
                self._playlist_total = total
                self._playlist_done  = current - 1
            self._emit_progress(0.0, "", "")
            return

        m = self._RE_PERCENT.search(line)
        if m:
            pct   = float(m.group(1))
            speed = eta = ""
            m2    = self._RE_SPEED_ETA.search(line)
            if m2:
                speed, eta = m2.group(1), m2.group(2)
            self._emit_progress(pct, speed, eta)

    def _emit_progress(self, item_pct: float, speed: str, eta: str) -> None:
        if self._playlist_total > 0:
            overall = (
                (self._playlist_done + item_pct / 100.0)
                / self._playlist_total
                * 100.0
            )
            self.task.percent = overall
        else:
            self.task.percent = item_pct

        self.task.speed = speed
        self.task.eta   = eta
        self._on_progress(self.task, self.task.percent, speed, eta)

    def _remove_part_files(self) -> None:
        time.sleep(0.2)
        try:
            out_path = getattr(self.task, "_output_path", None)
            if not out_path:
                return

            base = os.path.dirname(out_path)
            name = os.path.basename(out_path)

            for ext in (".part", ".ytdl", ".temp"):
                part_file = os.path.join(base, name + ext)
                if os.path.isfile(part_file):
                    try:
                        os.remove(part_file)
                    except OSError:
                        pass

            for f in os.listdir(base):
                if f.startswith(name) and (f.endswith(".frag") or f.endswith(".fragidx")):
                    try:
                        os.remove(os.path.join(base, f))
                    except OSError:
                        pass

        except Exception as exc:
            log.debug("_remove_part_files: %s", exc)


# ══════════════════════════════════════════════════════════════════════════════
#  §12  REUSABLE UI WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class StepIndicator(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, number: int, label: str, **kw) -> None:
        super().__init__(parent, fg_color="transparent", **kw)
        sz, sp = T.Size, T.Space

        circle = ctk.CTkFrame(
            self,
            width         = UIScale.sm(sz.STEP_CIR),
            height        = UIScale.sm(sz.STEP_CIR),
            corner_radius = UIScale.sm(sz.STEP_CIR_R),
            fg_color      = "transparent",
            border_width  = 1,
            border_color  = T.Color.BORDER_STEP,
        )
        circle.pack_propagate(False)
        circle.pack(side="left", padx=(0, UIScale.pm(sp.STEP_CIR_R)))

        ctk.CTkLabel(
            circle,
            text       = str(number),
            font       = ("Segoe UI", UIScale.fm(T.Font.STEP_NUM), "bold"),
            text_color = T.Color.TEXT_DIM,
        ).pack(expand=True)

        ctk.CTkLabel(
            self,
            text       = label,
            font       = ("Segoe UI", UIScale.fm(T.Font.STEP_LABEL)),
            text_color = T.Color.TEXT_MID,
            anchor     = "w",
        ).pack(side="left")


class QueueRow(ctk.CTkFrame):
    def __init__(
        self,
        parent          : ctk.CTkScrollableFrame,
        task            : DownloadTask,
        on_remove       : Callable[[], None],
        is_running_func : Callable[[], bool],
        **kw,
    ) -> None:
        super().__init__(
            parent,
            fg_color      = T.Color.BG_ROW,
            corner_radius = UIScale.sm(T.Size.QUEUE_ROW_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
            **kw,
        )
        self.task          = task
        self._on_remove    = on_remove
        self._is_running   = is_running_func
        self._saved_folder = None
        self._sub_text     = ""
        self._build()

    def _build(self) -> None:
        sz, sp = T.Size, T.Space
        accent = T.Color.MP3_ACTIVE if self.task.mode == "MP3" else T.Color.MP4_ACTIVE

        self._side_bar = ctk.CTkFrame(
            self, width=UIScale.sm(3), fg_color=accent, corner_radius=0)
        self._side_bar.place(relx=0, rely=0.1, relheight=0.8)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(
            row=0, column=0, sticky="ew",
            padx=(UIScale.pm(sp.ROW_PX) + UIScale.sm(5), UIScale.pm(sp.ROW_BADGE_PX)),
            pady=UIScale.pm(sp.ROW_PY),
        )
        text_frame.grid_columnconfigure(0, weight=1)

        self._title_lbl = ctk.CTkLabel(
            text_frame,
            text       = "",
            font       = ("Segoe UI", UIScale.fm(T.Font.ROW_TITLE), "bold"),
            text_color = T.Color.TEXT_BRIGHT,
            anchor     = "w",
            justify    = "left",
        )
        self._title_lbl.grid(row=0, column=0, sticky="ew")

        self._info_lbl = ctk.CTkLabel(
            text_frame,
            text       = "",
            font       = ("Segoe UI", UIScale.fm(T.Font.ROW_INFO)),
            text_color = T.Color.TEXT_DIM,
            anchor     = "w",
            justify    = "left",
        )
        self._info_lbl.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=(0, UIScale.pm(sp.ROW_R_PX)))

        self._badge_btn = ctk.CTkButton(
            right,
            text          = "0%",
            width         = UIScale.sm(sz.ROW_BADGE_W),
            height        = UIScale.sm(sz.ROW_BADGE_H),
            corner_radius = UIScale.sm(sz.ROW_BADGE_R),
            font          = ("Segoe UI", UIScale.fm(T.Font.ROW_BADGE), "bold"),
            text_color    = accent,
            fg_color      = T.Color.BG_ROW,
            hover_color   = T.Color.BG_ROW,
            border_width  = 0,
            command       = lambda: None,
        )
        self._badge_btn.pack(side="left", padx=(0, UIScale.pm(sp.ROW_BADGE_PX)))

        self._remove_btn = ctk.CTkButton(
            right,
            text          = "✕",
            width         = UIScale.sm(sz.ROW_REM_W),
            height        = UIScale.sm(sz.ROW_REM_H),
            corner_radius = UIScale.sm(sz.ROW_REM_R),
            fg_color      = "transparent",
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = T.Color.TEXT_DIM,
            font          = ("Segoe UI", UIScale.fm(T.Font.ROW_BADGE)),
            command       = self._click_remove,
        )
        self._remove_btn.pack(side="left")

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        return text[:max_chars - 1] + "…" if len(text) > max_chars else text

    def _available_title_width(self) -> int:
        try:
            w = self.winfo_toplevel().winfo_width()
            if w > 0:
                return max(100, w - UIScale.sm(120))
        except Exception:
            pass
        return UIScale.sm(440)

    def _update_text(self) -> None:
        status = self.task.status
        base   = self.task.title or self.task.url

        if self.task.playlist_name:
            short = self.task.playlist_name[:28]
            if len(self.task.playlist_name) > 28:
                short += "…"
            full = f"[{short}]  {base}"
        else:
            full = base

        avail    = self._available_title_width()
        char_est = max(6, UIScale.fm(T.Font.ROW_TITLE) - 2)
        self._title_lbl.configure(text=self._truncate(full, avail // char_est))

        parts = [f"Convert to {self.task.mode}"]
        if self.task.filesize_str and self.task.filesize_str != "Unknown":
            parts.append(self.task.filesize_str)
        if self.task.duration:
            parts.append(self.task.duration)
        if self._sub_text and status in (TaskStatus.DOWNLOADING, TaskStatus.FETCHING):
            parts.append(self._sub_text)
        if status == TaskStatus.DONE:
            parts.append("✅ Done")
        elif status == TaskStatus.FAILED:
            parts.append(f"❌ {self.task.error[:32]}")
        elif status == TaskStatus.CANCELLED:
            parts.append("⊘ Cancelled")

        self._info_lbl.configure(text="  ·  ".join(parts))

        error_color = status == TaskStatus.FAILED
        self._title_lbl.configure(
            text_color=T.Color.TEXT_ERROR if error_color else T.Color.TEXT_BRIGHT)
        self._info_lbl.configure(
            text_color=T.Color.TEXT_ERROR if error_color else T.Color.TEXT_DIM)

    def _click_remove(self) -> None:
        if self.task.status not in ACTIVE_STATUSES:
            self._on_remove()

    def _open_folder(self, _event=None) -> None:
        open_in_explorer(self._saved_folder or getattr(self.task, "save_path", ""))

    def refresh(self, sub_text: str = "", percent: Optional[float] = None) -> None:
        sz     = T.Size
        pct    = self.task.percent if percent is None else percent
        accent = T.Color.MP3_ACTIVE if self.task.mode == "MP3" else T.Color.MP4_ACTIVE
        status = self.task.status

        self._sub_text = sub_text
        if self.task.save_path:
            self._saved_folder = self.task.save_path

        try:
            self._side_bar.configure(fg_color=accent)
        except Exception:
            pass

        if status == TaskStatus.DONE and pct >= 99.9:
            self._badge_btn.configure(
                text          = "📌",
                text_color    = accent,
                width         = UIScale.sm(sz.ROW_REM_W),
                height        = UIScale.sm(sz.ROW_REM_H),
                cursor        = "hand2",
                command       = self._open_folder,
                fg_color      = T.Color.BG_ROW,
                hover_color   = T.Color.BTN_SUBTLE_HV,
                border_width  = 0,
            )
        else:
            self._badge_btn.configure(
                text         = f"{int(pct)}%",
                text_color   = accent,
                width        = UIScale.sm(sz.ROW_BADGE_W),
                height        = UIScale.sm(sz.ROW_BADGE_H),
                cursor       = "arrow",
                command      = lambda: None,
                fg_color     = T.Color.BG_ROW,
                hover_color  = T.Color.BG_ROW,
                border_width = 0,
            )

        self._update_text()

        disable_remove = (
            (self._is_running() if self._is_running else False)
            or status in ACTIVE_STATUSES
        )
        self._remove_btn.configure(state="disabled" if disable_remove else "normal")


# ══════════════════════════════════════════════════════════════════════════════
#  §13  THEMED DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class DialogStyle(NamedTuple):
    accent  : str
    symbol  : str
    icon_bg : str
    hover   : str


class ThemedDialog(ctk.CTkToplevel):
    _STYLES: Dict[str, DialogStyle] = {
        "info"        : DialogStyle(*T.Color.DLG_INFO),
        "warning"     : DialogStyle(*T.Color.DLG_WARNING),
        "error"       : DialogStyle(*T.Color.DLG_ERROR),
        "success_mp3" : DialogStyle(*T.Color.DLG_SUCCESS_MP3),
        "success_mp4" : DialogStyle(*T.Color.DLG_SUCCESS_MP4),
        "about"       : DialogStyle(*T.Color.DLG_ABOUT),
    }

    def __init__(
        self,
        master           : ctk.CTk,
        title            : str,
        message          : str,
        kind             : str           = "info",
        open_folder_path : Optional[str] = None,
        height           : Optional[int] = None,
        donate_link      : Optional[str] = None,
        inner_title      : Optional[str] = None,
        width_override   : Optional[int] = None,
    ) -> None:
        super().__init__(master)
        self.attributes("-alpha", 0)
        self.title(title)
        if IS_WINDOWS and os.path.isfile(ICON_PATH):
            self.after(200, lambda: self.iconbitmap(ICON_PATH))
        self.resizable(False, False)
        self.configure(fg_color=T.Color.BG_ROOT)
        self.grab_set()

        self._width_override = width_override
        self._dlg_width      = self._set_geometry(master, open_folder_path, height, kind)
        self._build_content(title, message, kind, open_folder_path, donate_link, inner_title)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.attributes("-alpha", 1)
        self.focus_force()

    def _set_geometry(self, master, open_folder_path, height_override, kind: str = "info") -> int:
        self.update_idletasks()
        sw, sh = get_logical_screen(self)
        td     = T.Dialog

        if kind == "about":
            w = min(
                max(UIScale.s(td.ABOUT_W_ABS_MIN), int(sw * td.ABOUT_W_PCT)),
                int(sw * td.ABOUT_W_MAX_PCT),
                UIScale.s(td.ABOUT_W_ABS_MAX),
            )
            h = min(
                max(UIScale.s(td.ABOUT_H_ABS_MIN), int(sh * td.ABOUT_H_PCT)),
                int(sh * td.ABOUT_H_MAX_PCT),
                UIScale.s(td.ABOUT_H_ABS_MAX),
            )
            if self._width_override:
                w = min(
                    max(UIScale.s(td.ABOUT_W_ABS_MIN), self._width_override),
                    int(sw * td.ABOUT_W_MAX_PCT),
                    UIScale.s(td.ABOUT_W_ABS_MAX),
                )
            if height_override:
                h = min(
                    max(UIScale.s(td.ABOUT_H_ABS_MIN), height_override),
                    int(sh * td.ABOUT_H_MAX_PCT),
                    UIScale.s(td.ABOUT_H_ABS_MAX),
                )
            self.minsize(
                min(UIScale.s(td.ABOUT_W_ABS_MIN), int(sw * td.ABOUT_W_MIN_PCT)),
                min(UIScale.s(td.ABOUT_H_ABS_MIN), int(sh * td.ABOUT_H_MIN_PCT)),
            )
            self.maxsize(
                min(int(sw * td.ABOUT_W_MAX_PCT), UIScale.s(td.ABOUT_W_ABS_MAX)),
                min(int(sh * td.ABOUT_H_MAX_PCT), UIScale.s(td.ABOUT_H_ABS_MAX)),
            )
        else:
            w = (
                self._width_override
                if self._width_override
                else min(
                    max(UIScale.s(td.W_ABS_MIN), int(sw * td.W_MIN_PCT)),
                    int(sw * td.W_MAX_PCT),
                )
            )
            h_base = td.H_FOLDER_MIN if open_folder_path else td.H_ABS_MIN
            h      = min(
                max(UIScale.s(h_base), int(sh * td.H_MIN_PCT)),
                int(sh * td.H_MAX_PCT),
            )
            if height_override:
                h = max(h, height_override)

        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()  - w) // 2
        y = master.winfo_y() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        return w

    def _build_content(
        self,
        title, message, kind, open_folder_path, donate_link, inner_title,
    ) -> None:
        style      = self._STYLES.get(kind, self._STYLES["info"])
        show_title = inner_title if inner_title is not None else title
        sz, sp     = T.Size, T.Space
        wrap       = max(UIScale.s(200), self._dlg_width - UIScale.s(150))
        is_about   = kind == "about"

        shell = ctk.CTkFrame(
            self,
            fg_color      = T.Color.BG_CARD,
            corner_radius = UIScale.s(sz.PANEL_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
        )
        shell.pack(
            fill="both", expand=True,
            padx=UIScale.p(sp.DLG_SHELL_P),
            pady=UIScale.p(sp.DLG_SHELL_P),
        )

        ctk.CTkFrame(
            shell,
            height        = UIScale.s(3 if is_about else sz.ACCENT_H),
            fg_color      = style.accent,
            corner_radius = 0,
        ).pack(fill="x", padx=1, pady=(UIScale.p(12), 0))

        body = ctk.CTkFrame(shell, fg_color="transparent")
        body.pack(
            fill="both", expand=True,
            padx=UIScale.p(sp.DLG_BODY_PX),
            pady=(UIScale.p(sp.DLG_BODY_PY), UIScale.p(sp.DLG_BODY_PY)),
        )

        icon_w = sz.ABOUT_ICON_W if is_about else sz.DLG_ICON_SZ
        icon_h = sz.ABOUT_ICON_H if is_about else sz.DLG_ICON_SZ
        icon_r = sz.ABOUT_ICON_R if is_about else sz.DLG_ICON_R
        icon_f = T.Font.ABOUT_ICON if is_about else T.Font.DLG_ICON

        icon_frame = ctk.CTkFrame(
            body,
            width         = UIScale.s(icon_w),
            height        = UIScale.s(icon_h),
            corner_radius = UIScale.s(icon_r),
            fg_color      = style.icon_bg,
            border_width  = 1,
            border_color  = style.accent,
        )
        icon_frame.pack_propagate(False)
        icon_frame.pack(side="left", anchor="n", padx=(0, UIScale.p(sp.DLG_ICON_R)))

        icon_lbl = ctk.CTkLabel(
            icon_frame,
            text       = style.symbol,
            font       = ("Segoe UI", UIScale.f(icon_f), "bold"),
            text_color = style.accent,
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(body, fg_color="transparent")
        if is_about:
            text_frame.pack(side="left", fill="both", expand=True, pady=(UIScale.p(-4), 0))
        else:
            text_frame.pack(side="left", fill="both", expand=True)

        title_lbl  = None
        title_font = T.Font.ABOUT_TITLE if is_about else T.Font.DLG_TITLE

        if show_title and show_title.strip():
            title_lbl = ctk.CTkLabel(
                text_frame,
                text       = show_title,
                font       = ("Segoe UI", UIScale.f(title_font), "bold"),
                text_color = T.Color.TEXT_BRIGHT,
                anchor     = "w",
            )
            title_lbl.pack(fill="x")
            msg_pady: Tuple[int, int] = (UIScale.p(sp.DLG_MSG_PY), 0)
        else:
            msg_pady = (0, 0)

        msg_font = T.Font.ABOUT_MSG if is_about else T.Font.DLG_MSG

        if is_about:
            scroll_container = ctk.CTkScrollableFrame(
                text_frame,
                fg_color                     = "transparent",
                corner_radius                = 0,
                border_width                 = 0,
                scrollbar_button_color       = T.Color.BORDER,
                scrollbar_button_hover_color = T.Color.BORDER_STEP,
            )
            scroll_container.pack(fill="both", expand=True, pady=msg_pady)

            msg_lbl = ctk.CTkLabel(
                scroll_container,
                text       = message,
                font       = ("Segoe UI", UIScale.f(msg_font)),
                text_color = T.Color.TEXT_MID,
                justify    = "left",
                anchor     = "w",
                wraplength = wrap,
            )
            msg_lbl.pack(fill="x", padx=(0, UIScale.p(6)), pady=(0, UIScale.p(4)))
        else:
            scroll_container = None
            msg_lbl = ctk.CTkLabel(
                text_frame,
                text       = message,
                font       = ("Segoe UI", UIScale.f(msg_font)),
                text_color = T.Color.TEXT_MID,
                justify    = "left",
                anchor     = "w",
                wraplength = wrap,
            )
            msg_lbl.pack(fill="both", expand=True, pady=msg_pady)

        if is_about:
            self._wire_about_resize(msg_lbl, icon_lbl, title_lbl, scroll_container)

        self._add_button_row(shell, style, kind, open_folder_path, donate_link)

    def _wire_about_resize(self, msg_lbl, icon_lbl, title_lbl, scroll_container=None) -> None:
        td, tf = T.Dialog, T.Font

        def _compute_fonts(win_w: int, win_h: int) -> Tuple[int, int, int]:
            ref_w = max(1, UIScale.s(td.ABOUT_REF_W))
            ref_h = max(1, UIScale.s(td.ABOUT_REF_H))
            scale = min(win_w / ref_w, win_h / ref_h)
            scale = max(td.ABOUT_SCALE_MIN, min(td.ABOUT_SCALE_MAX, scale))
            base  = max(
                UIScale.f(10),
                min(UIScale.f(tf.ABOUT_MAX), round(UIScale.f(tf.ABOUT_MSG) * scale)),
            )
            return (
                base,
                min(UIScale.f(tf.ABOUT_MAX + 1), base + UIScale.f(1)),
                min(UIScale.f(tf.ABOUT_ICON),    base + UIScale.f(4)),
            )

        def _on_resize(_event=None) -> None:
            if _event is not None and _event.widget is not self:
                return
            try:
                if not self.winfo_exists():
                    return
                win_w = max(1, self.winfo_width())
                win_h = max(1, self.winfo_height())
            except Exception:
                return

            base, title_f, icon_f = _compute_fonts(win_w, win_h)
            new_wrap = max(UIScale.s(180), win_w - UIScale.s(140))
            msg_lbl.configure(font=("Segoe UI", base), wraplength=new_wrap)
            icon_lbl.configure(font=("Segoe UI", icon_f, "bold"))
            if title_lbl:
                title_lbl.configure(font=("Segoe UI", title_f, "bold"))

        self.bind("<Configure>", _on_resize)
        self.after(100, _on_resize)

    def _add_donate_row(self, parent, donate_link) -> Tuple[ctk.CTkLabel, ctk.CTkButton]:
        sz, sp = T.Size, T.Space

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(
            fill="x",
            padx=UIScale.p(sp.DLG_BTN_PX),
            pady=(UIScale.p(sp.DONATE_PY), 0),
        )

        lbl = ctk.CTkLabel(
            row,
            text       = "💚  Support via ",
            font       = ("Segoe UI", UIScale.f(T.Font.DONATE_LBL)),
            text_color = T.Color.TEXT_DIM,
        )
        lbl.pack(side="left")

        btn = ctk.CTkButton(
            row,
            text          = "PayPal",
            font          = ("Segoe UI", UIScale.f(T.Font.DONATE_BTN), "bold"),
            text_color    = T.Color.TEXT_BRIGHT,
            fg_color      = T.Color.BG_INPUT,
            hover_color   = T.Color.BTN_SUBTLE_HV,
            width         = UIScale.s(sz.DONATE_BTN_W),
            height        = UIScale.s(sz.DONATE_BTN_H),
            corner_radius = UIScale.s(sz.DONATE_BTN_R),
            cursor        = "hand2",
            command       = lambda: webbrowser.open(donate_link),
        )
        btn.pack(side="left")
        return lbl, btn

    def _add_button_row(self, shell, style, kind, open_folder_path, donate_link=None) -> None:
        sz, sp   = T.Size, T.Space
        is_about = kind == "about"

        if donate_link and is_about:
            self._add_donate_row(shell, donate_link)

        row = ctk.CTkFrame(shell, fg_color="transparent")
        row.pack(
            fill="x",
            padx=UIScale.p(sp.DLG_BTN_PX),
            pady=(UIScale.p(sp.DLG_BTN_PY_T), UIScale.p(sp.DLG_BTN_PY_B)),
        )

        ctk.CTkButton(
            row,
            text          = "OK",
            height        = UIScale.s(sz.ABOUT_OK_H if is_about else sz.DLG_OK_H),
            width         = UIScale.s(sz.ABOUT_OK_W  if is_about else sz.DLG_OK_W),
            corner_radius = UIScale.s(sz.DLG_OK_R),
            fg_color      = T.Color.TEXT_BRIGHT if is_about else style.accent,
            hover_color   = T.Color.BTN_SUBTLE_HV if is_about else style.hover,
            text_color    = T.Color.BG_CARD if is_about else "#ffffff",
            font          = ("Segoe UI", UIScale.f(T.Font.DLG_BTN), "bold"),
            command       = self.destroy,
        ).pack(side="right")

        if open_folder_path:
            ctk.CTkButton(
                row,
                text          = "Open Folder",
                height        = UIScale.s(sz.DLG_FOLDER_H),
                width         = UIScale.s(sz.DLG_FOLDER_W),
                corner_radius = UIScale.s(sz.DLG_FOLDER_R),
                fg_color      = T.Color.BG_INPUT,
                hover_color   = T.Color.BTN_SUBTLE_HV,
                text_color    = T.Color.TEXT_MID,
                border_width  = 1,
                border_color  = T.Color.BORDER,
                font          = ("Segoe UI", UIScale.f(T.Font.DLG_MSG)),
                command       = lambda p=open_folder_path: open_in_explorer(p, create=True),
            ).pack(side="right", padx=(0, UIScale.p(8)))

    def show(self) -> None:
        self.wait_window(self)


# ══════════════════════════════════════════════════════════════════════════════
#  §14  HISTORY PANEL
# ══════════════════════════════════════════════════════════════════════════════

class HistoryPanel(ctk.CTkToplevel):
    _STATUS_ICONS: Dict[str, Tuple[str, str]] = {
        "done"  : ("✓", T.Color.MP3_ACTIVE),
        "failed": ("✕", T.Color.BTN_DANGER),
    }
    _DEFAULT_ICON: Tuple[str, str] = ("⊘", T.Color.BTN_WARN)

    def __init__(self, master: ctk.CTk, history: DownloadHistory) -> None:
        super().__init__(master)
        self.attributes("-alpha", 0)
        self.title("Download History")
        if IS_WINDOWS and os.path.isfile(ICON_PATH):
            self.after(200, lambda: self.iconbitmap(ICON_PATH))
        self.resizable(False, False)
        self.configure(fg_color=T.Color.BG_ROOT)
        self._history = history

        sw, sh = get_logical_screen(self)
        td     = T.Dialog
        w = min(
            max(UIScale.s(td.HIST_W_ABS_MIN), int(sw * td.HIST_W_MIN_PCT)),
            int(sw * td.HIST_W_MAX_PCT),
        )
        h = min(
            max(UIScale.s(td.HIST_H_ABS_MIN), int(sh * td.HIST_H_MIN_PCT)),
            int(sh * td.HIST_H_MAX_PCT),
        )
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()  - w) // 2
        y = master.winfo_y() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(UIScale.s(td.HIST_W_ABS_MIN), UIScale.s(td.HIST_H_ABS_MIN))

        self._build_ui()
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.attributes("-alpha", 1)

    def _build_ui(self) -> None:
        sz, sp = T.Size, T.Space

        shell = ctk.CTkFrame(
            self,
            fg_color      = T.Color.BG_CARD,
            corner_radius = UIScale.s(sz.PANEL_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
        )
        shell.pack(
            fill="both", expand=True,
            padx=UIScale.p(sp.HIST_SHELL_P),
            pady=UIScale.p(sp.HIST_SHELL_P),
        )
        shell.grid_rowconfigure(0, weight=0)
        shell.grid_rowconfigure(1, weight=1)
        shell.grid_rowconfigure(2, weight=0)
        shell.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(
            shell,
            height        = UIScale.s(sz.ACCENT_H),
            fg_color      = T.Color.HIST_MAIN,
            corner_radius = 0,
        ).grid(row=0, column=0, sticky="ew", padx=1, pady=(UIScale.p(12), 0))

        self._scroll = ctk.CTkScrollableFrame(
            shell,
            fg_color      = T.Color.BG_INPUT,
            corner_radius = UIScale.s(12),
            border_width  = 1,
            border_color  = T.Color.BORDER,
        )
        self._scroll.grid(
            row=1, column=0, sticky="nsew",
            padx=UIScale.p(sp.HIST_BODY_PX),
            pady=(UIScale.p(sp.HIST_BODY_PY), UIScale.p(6)),
        )
        self._render()

        btn_row = ctk.CTkFrame(shell, fg_color="transparent")
        btn_row.grid(
            row=2, column=0, sticky="ew",
            padx=UIScale.p(sp.HIST_BTN_PX),
            pady=(UIScale.p(sp.HIST_BTN_PY), UIScale.p(sp.HIST_BTN_PY + 4)),
        )
        ctk.CTkButton(
            btn_row,
            text          = "Clear All",
            height        = UIScale.s(28),
            width         = UIScale.s(80),
            corner_radius = UIScale.s(8),
            fg_color      = T.Color.HIST_MAIN,
            hover_color   = T.Color.HIST_HOVER,
            text_color    = T.Color.TEXT_BRIGHT,
            font          = ("Segoe UI", UIScale.f(T.Font.DLG_BTN), "bold"),
            command       = self._clear_and_close,
        ).pack(side="right")

    def _clear_and_close(self) -> None:
        self._history.clear()
        self.destroy()

    def _render(self) -> None:
        for w in self._scroll.winfo_children():
            w.destroy()

        self._resize_callbacks = []
        records = self._history.items

        if not records:
            ctk.CTkLabel(
                self._scroll,
                text       = "No downloads yet.",
                text_color = T.Color.TEXT_DIM,
                font       = ("Segoe UI", UIScale.f(T.Font.DLG_MSG)),
            ).pack(pady=30)
        else:
            for record in records:
                self._render_row(record)

            def _on_any_resize(_event=None) -> None:
                for cb in self._resize_callbacks:
                    cb()

            self._scroll.bind("<Configure>", _on_any_resize, add="+")

        self._scroll.update_idletasks()
        self._scroll._parent_canvas.configure(
            scrollregion=self._scroll._parent_canvas.bbox("all")
        )

    def _render_row(self, record: Dict[str, Any]) -> None:
        sz, sp             = T.Size, T.Space
        status             = record.get("status", "done")
        mode               = record.get("mode", "")
        icon, base_icon_col = self._STATUS_ICONS.get(status, self._DEFAULT_ICON)

        if status == "done" and mode in MODE_STYLES:
            mode_color = MODE_STYLES[mode].active
            border_col = MODE_STYLES[mode].accent
            icon_col   = mode_color
        else:
            border_col = T.Color.BORDER
            icon_col   = base_icon_col

        row = ctk.CTkFrame(
            self._scroll,
            fg_color      = T.Color.BG_HIST_ROW,
            corner_radius = UIScale.s(sz.HIST_ROW_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
        )
        row.pack(fill="x", padx=UIScale.p(sp.HIST_ROW_PX), pady=(sp.HIST_ROW_PY, sp.HIST_ROW_PY))
        row.grid_columnconfigure(0, weight=0)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=0)

        icon_frame = ctk.CTkFrame(
            row,
            width         = UIScale.s(sz.HIST_ICON),
            height        = UIScale.s(sz.HIST_ICON),
            corner_radius = UIScale.s(sz.HIST_ICON_R),
            fg_color      = T.Color.BG_INPUT,
            border_width  = 1,
            border_color  = border_col,
        )
        icon_frame.grid_propagate(False)
        icon_frame.grid(
            row=0, column=0,
            padx=(UIScale.p(sp.HIST_ICON_PX), UIScale.p(sp.HIST_ICON_R)),
            pady=UIScale.p(sp.HIST_BODY_PY),
        )
        ctk.CTkLabel(
            icon_frame,
            text       = icon,
            font       = ("Segoe UI", UIScale.f(T.Font.HIST_ICON), "bold"),
            text_color = icon_col,
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(
            row=0, column=1, sticky="ew",
            padx=(0, UIScale.p(sp.HIST_ICON_PX)),
            pady=UIScale.p(sp.HIST_BODY_PY),
        )

        original  = record.get("title", record.get("url", "Unknown"))
        font_size = T.Font.HIST_TITLE

        def _get_width() -> int:
            try:
                w = self._scroll.winfo_width()
                return w - UIScale.s(90) if w > 0 else UIScale.s(280)
            except Exception:
                return UIScale.s(280)

        title_lbl = ctk.CTkLabel(
            info,
            text       = self._truncate(original, _get_width(), font_size),
            font       = ("Segoe UI", UIScale.f(font_size)),
            text_color = T.Color.TEXT_BRIGHT,
            anchor     = "w",
            justify    = "left",
        )
        title_lbl.pack(fill="x", pady=(0, UIScale.p(3)))

        def _on_resize(
            _event=None, _orig=original, _fs=font_size, _lbl=title_lbl,
        ) -> None:
            new_w = self._scroll.winfo_width() - UIScale.s(90)
            if new_w > UIScale.s(40):
                _lbl.configure(text=self._truncate(_orig, new_w, _fs))

        self._resize_callbacks.append(_on_resize)

        ctk.CTkLabel(
            info,
            text       = f"{mode}  ·  {record.get('time', '')}",
            font       = ("Segoe UI", UIScale.f(T.Font.HIST_META)),
            text_color = T.Color.TEXT_DIM,
            anchor     = "w",
        ).pack(fill="x")

        pin_accent = T.Color.MP3_ACTIVE if mode == "MP3" else T.Color.MP4_ACTIVE
        ctk.CTkButton(
            row,
            text          = "📌",
            width         = UIScale.s(sz.HIST_PIN),
            height        = UIScale.s(sz.HIST_PIN),
            corner_radius = UIScale.s(sz.HIST_PIN_R),
            fg_color      = "transparent",
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = pin_accent,
            font          = ("Segoe UI", UIScale.f(14)),
            command       = lambda p=record.get("save_path", ""): open_in_explorer(p),
        ).grid(
            row=0, column=2,
            padx=(0, UIScale.p(sp.HIST_ICON_PX)),
            pady=UIScale.p(sp.HIST_BODY_PY),
        )

    @staticmethod
    def _truncate(text: str, avail_px: int, font_size: int) -> str:
        if not text:
            return ""
        if avail_px <= 0:
            return text[:60] + "…" if len(text) > 63 else text
        char_w = max(5, font_size - 3)
        max_c  = max(15, avail_px // char_w)
        return text[:max_c - 1] + "…" if len(text) > max_c else text


# ══════════════════════════════════════════════════════════════════════════════
#  §15  ACTION HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

class AddToQueueHandler:
    def __init__(
        self,
        url_entry         : ctk.CTkEntry,
        add_button        : ctk.CTkButton,
        queue_manager     : QueueManager,
        tools             : ToolManager,
        current_mode_func : Callable[[], str],
        on_tasks_added    : Callable[[List[DownloadTask]], None],
        show_dialog_func  : Callable[[str, str, str], None],
        root              : ctk.CTk,
    ) -> None:
        self._entry       = url_entry
        self._btn         = add_button
        self._queue       = queue_manager
        self._tools       = tools
        self._mode        = current_mode_func
        self._on_added    = on_tasks_added
        self._show_dialog = show_dialog_func
        self._root        = root
        self._anim_job    : Optional[str] = None

    def execute(self) -> None:
        raw = self._entry.get().strip()
        if not raw:
            return

        urls = [u.strip() for u in raw.splitlines() if u.strip()]
        for url in urls:
            ok, reason = validate_url(url)
            if not ok:
                self._show_dialog("Invalid URL", f"Not a valid URL:\n{url[:80]}", "warning")
                return

        self._set_busy(True)
        threading.Thread(target=self._resolve, args=(urls,), daemon=True).start()

    def _set_busy(self, busy: bool) -> None:
        if busy:
            self._entry.configure(state="disabled")
            self._btn.configure(state="disabled", text=T.Anim.ADD_FRAMES[0])
            self._animate(1)
        else:
            if self._anim_job:
                self._root.after_cancel(self._anim_job)
                self._anim_job = None
            self._entry.configure(state="normal")
            self._btn.configure(state="normal", text="Add")

    def _animate(self, frame: int) -> None:
        self._btn.configure(text=T.Anim.ADD_FRAMES[frame % len(T.Anim.ADD_FRAMES)])
        self._anim_job = self._root.after(T.Anim.ADD_INTERVAL_MS, self._animate, frame + 1)

    def _resolve(self, urls: List[str]) -> None:
        resolved    : List[DownloadTask] = []
        failed_urls : List[str]          = []
        mode = self._mode()

        for url in urls:
            try:
                proc = subprocess.run(
                    [
                        self._tools.yt_dlp, "--no-update", "--quiet",
                        "--flat-playlist",
                        "--print", "%(title)s\t%(url)s\t%(duration_string)s\t%(filesize_approx)s",
                        "--print", "playlist_title",
                        url,
                    ],
                    capture_output = True,
                    text           = True,
                    encoding       = "utf-8",
                    errors         = "replace",
                    timeout        = 30,
                    **_SUBPROCESS_FLAGS,
                )
            except Exception as exc:
                log.debug("_resolve: %s", exc)
                failed_urls.append(url)
                continue

            all_lines  = [ln for ln in proc.stdout.splitlines() if ln.strip()]
            tab_lines  = [ln for ln in all_lines if "\t" in ln]
            meta_lines = [ln.strip() for ln in all_lines if "\t" not in ln]

            is_list  = len(tab_lines) > 1
            pl_title = meta_lines[0] if (is_list and meta_lines) else ""

            tasks = self._parse_lines(tab_lines, url, mode, pl_title)
            if tasks:
                resolved.extend(tasks)
            else:
                failed_urls.append(url)

        if resolved:
            self._root.after(0, self._finish, resolved)
        else:
            self._root.after(0, self._set_busy, False)
            self._root.after(0, self._entry.delete, 0, "end")
            msg = (
                "Cannot process:\n" + "\n".join(failed_urls[:5])
                if failed_urls
                else "No valid video or playlist found."
            )
            self._root.after(0, self._show_dialog, "No content found", msg, "warning")

    def _parse_lines(self, tab_lines, fallback_url, mode, playlist_title) -> List[DownloadTask]:
        tasks = []
        for line in tab_lines:
            parts    = line.split("\t")
            title    = parts[0].strip() if len(parts) > 0 else ""
            url      = parts[1].strip() if len(parts) > 1 else ""
            duration = parts[2].strip() if len(parts) > 2 else ""
            filesize = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

            if duration and not re.match(r"^(\d+:)?\d+:\d+$", duration):
                duration = ""
            if not url or url.startswith("NA"):
                url = fallback_url
            if duration.startswith("0:"):
                duration = duration[2:]

            tasks.append(DownloadTask(
                url           = url,
                mode          = mode,
                title         = title or url,
                duration      = duration,
                filesize      = filesize,
                filesize_str  = format_filesize(filesize),
                playlist_name = playlist_title,
            ))
        return tasks

    def _finish(self, tasks: List[DownloadTask]) -> None:
        self._set_busy(False)
        self._queue.add_tasks(tasks)
        self._on_added(tasks)
        self._entry.delete(0, "end")


class StartStopQueueHandler:
    def __init__(
        self,
        download_button  : ctk.CTkButton,
        queue_controller : "QueueController",
        on_stop_callback : Optional[Callable[[], None]] = None,
    ) -> None:
        self._btn        = download_button
        self._controller = queue_controller
        self._on_stop    = on_stop_callback

    def execute(self) -> None:
        if self._controller.is_running:
            if self._on_stop:
                self._on_stop()
            self._controller.stop()
        else:
            self._controller.start()


class SetModeHandler:
    def __init__(
        self,
        mp3_button        : ctk.CTkButton,
        mp4_button        : ctk.CTkButton,
        icon_label        : ctk.CTkLabel,
        add_button        : ctk.CTkButton,
        download_button   : ctk.CTkButton,
        path_label        : ctk.CTkLabel,
        get_save_path     : Callable[[str], str],
        is_running        : Callable[[], bool],
        set_current_mode  : Callable[[str], None],
        update_path_label : Callable[[], None],
    ) -> None:
        self._mp3         = mp3_button
        self._mp4         = mp4_button
        self._icon        = icon_label
        self._add         = add_button
        self._download    = download_button
        self._path_lbl    = path_label
        self._get_path    = get_save_path
        self._is_running  = is_running
        self._set_mode    = set_current_mode
        self._update_path = update_path_label

    def execute(self, mode: str) -> None:
        style            = MODE_STYLES[mode]
        active, inactive = (
            (self._mp3, self._mp4) if mode == "MP3"
            else (self._mp4, self._mp3)
        )
        self._set_mode(mode)

        active.configure(
            fg_color     = style.accent,
            hover_color  = style.hover,
            text_color   = "#ffffff",
            border_width = 0,
        )
        inactive.configure(
            fg_color     = T.Color.MODE_OFF,
            hover_color  = T.Color.MODE_OFF_HV,
            text_color   = T.Color.TEXT_DIM,
            border_width = 1,
            border_color = T.Color.BORDER,
        )
        self._icon.configure(text_color=style.active)
        self._add.configure(
            fg_color=style.accent, hover_color=style.hover, text_color="#ffffff")

        if not self._is_running():
            self._download.configure(
                fg_color=style.accent, hover_color=style.hover, text_color="#ffffff")

        self._update_path()


class ChangePathHandler:
    def __init__(
        self,
        path_label       : ctk.CTkLabel,
        get_save_path    : Callable[[], str],
        is_running       : Callable[[], bool],
        root             : ctk.CTk,
        on_paths_changed : Callable[[str, str], None],
    ) -> None:
        self._label      = path_label
        self._get_path   = get_save_path
        self._is_running = is_running
        self._root       = root
        self._on_changed = on_paths_changed

    def execute(self) -> None:
        if self._is_running():
            return
        default = os.path.join(os.path.expanduser("~"), "Downloads", "Universal Downloader")
        os.makedirs(default, exist_ok=True)
        chosen = filedialog.askdirectory(
            parent     = self._root,
            initialdir = default,
            title      = "Select Download Folder",
        )
        if not chosen:
            return
        self._on_changed(
            os.path.join(chosen, "Music"),
            os.path.join(chosen, "Videos"),
        )
        self._label.configure(text=f"📍  {self._get_path()}")


class ClearDoneHandler:
    def __init__(self, queue_manager: QueueManager, on_changed: Callable[[], None]) -> None:
        self._queue      = queue_manager
        self._on_changed = on_changed

    def execute(self) -> None:
        self._queue.remove_finished()
        self._on_changed()


class RemoveTaskHandler:
    def __init__(
        self,
        task          : DownloadTask,
        queue_manager : QueueManager,
        on_changed    : Callable[[], None],
    ) -> None:
        self._task       = task
        self._queue      = queue_manager
        self._on_changed = on_changed

    def execute(self) -> None:
        if self._task.status in ACTIVE_STATUSES:
            return
        self._queue.remove_task(self._task)
        self._on_changed()


class ShowHistoryHandler:
    def __init__(self, root: ctk.CTk, history: DownloadHistory) -> None:
        self._root    = root
        self._history = history

    def execute(self) -> None:
        HistoryPanel(self._root, self._history)


class ShowAboutHandler:
    _DONATE_LINK = "https://www.paypal.com/paypalme/mohamadbittar"

    _ABOUT_TEXT = (
       " Universal Downloader\n"
        " A powerful, open-source tool to download videos and audio from YouTube,\n"
        " SoundCloud, Vimeo, Twitch, TikTok, Twitter, Facebook, Instagram, and 20+ other sites.\n"
        " ─────────────────────────────────\n"
        " ■  MP3 (320 kbps) – high quality audio\n"
        " ■  MP4 (best quality) – video + audio\n"
        " ■  Queue: add multiple links and download them in order\n"
        " ■  Auto-retry on network errors (up to 2 attempts)\n"
        " ■  Per-item progress\n"
        " ■  Playlist support – each video gets its own queue entry\n"
        " ─────────────────────────────────\n"
        " Powered by:\n"
        " • yt-dlp (github.com/yt-dlp/yt-dlp)\n"
        " • FFmpeg (ffmpeg.org)\n"
        " ─────────────────────────────────\n"
        " LICENSE & USAGE\n"
        " ✔️ Completely free – no payment, no ads.\n"
        " ✔️ For personal, non‑commercial use only.\n"
        " ✔️ Not for redistribution or resale.\n"
        " ─────────────────────────────────\n"
        " Thank you for using Universal Downloader.\n"
        " Respect content owners – download only what you have the right to.\n"
        " ─────────────────────────────────\n"
        " Developed by: Bittar Tech Lab\n"
        " ──────────────\n"
        " SUPPORT THE DEVELOPER\n"
        " ✨ Donations are welcomed but never required.\n"
        " ✨ Any amount encourages me and is greatly appreciated."
    )

    def __init__(self, root: ctk.CTk) -> None:
        self._root = root

    def execute(self) -> None:
        ThemedDialog(
            self._root,
            title       = "About Universal Downloader",
            inner_title = "",
            message     = self._ABOUT_TEXT,
            kind        = "about",
            donate_link = self._DONATE_LINK,
        ).show()


class ClearUrlEntryHandler:
    def __init__(self, url_entry: ctk.CTkEntry) -> None:
        self._entry = url_entry

    def execute(self) -> None:
        self._entry.delete(0, "end")


class PasteHandler:
    def __init__(self, url_entry: ctk.CTkEntry, root: ctk.CTk) -> None:
        self._entry = url_entry
        self._root  = root

    def execute(self, _event=None) -> None:
        try:
            text = self._root.clipboard_get()
            self._entry.delete(0, "end")
            self._entry.insert(0, text)
        except tk.TclError:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  §16  UI BUILDER
# ══════════════════════════════════════════════════════════════════════════════

class AppUIBuilder:
    def __init__(self, root: ctk.CTk) -> None:
        self._root = root

        self.url_entry         : ctk.CTkEntry           = None   # type: ignore
        self.add_button        : ctk.CTkButton          = None   # type: ignore
        self.mp3_button        : ctk.CTkButton          = None   # type: ignore
        self.mp4_button        : ctk.CTkButton          = None   # type: ignore
        self.path_label        : ctk.CTkLabel           = None   # type: ignore
        self.path_button       : ctk.CTkButton          = None   # type: ignore
        self.history_button    : ctk.CTkButton          = None   # type: ignore
        self.about_button      : ctk.CTkButton          = None   # type: ignore
        self.download_button   : ctk.CTkButton          = None   # type: ignore
        self.clear_done_button : ctk.CTkButton          = None   # type: ignore
        self.queue_scroll      : ctk.CTkScrollableFrame = None   # type: ignore
        self.empty_label       : ctk.CTkLabel           = None   # type: ignore
        self.icon_label        : ctk.CTkLabel           = None   # type: ignore
        self._clear_entry_btn  : ctk.CTkButton          = None   # type: ignore
        self.main_frame        : ctk.CTkFrame           = None   # type: ignore

    def build(self, initial_save_path: str) -> None:
        sp   = T.Space
        main = ctk.CTkFrame(self._root, fg_color=T.Color.BG_ROOT)
        main.pack(
            fill="both", expand=True,
            padx=UIScale.pm(sp.WIN_PX),
            pady=UIScale.pm(sp.WIN_PY),
        )
        # Row 7 is reserved for the optional UpdateBanner
        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=0)
        main.grid_rowconfigure(2, weight=0)
        main.grid_rowconfigure(3, weight=0)
        main.grid_rowconfigure(4, weight=1)
        main.grid_rowconfigure(5, weight=0)
        main.grid_rowconfigure(6, weight=0)
        main.grid_rowconfigure(7, weight=0)   # UpdateBanner row
        main.grid_columnconfigure(0, weight=1)

        self.main_frame = main

        self._build_header(main)
        self._build_separator(main)
        self._build_url_card(main)
        self._build_mode_card(main)
        self._build_queue_panel(main)
        self._build_path_row(main, initial_save_path)
        self._build_start_button(main)

    @staticmethod
    def _card(parent: ctk.CTkFrame, corner_radius: int = None, **kwargs) -> ctk.CTkFrame:
        if corner_radius is None:
            corner_radius = UIScale.sm(T.Size.CARD_R)
        return ctk.CTkFrame(
            parent,
            fg_color      = T.Color.BG_CARD,
            corner_radius = corner_radius,
            border_width  = 1,
            border_color  = T.Color.BORDER,
            **kwargs,
        )

    @classmethod
    def _sec_btn_style(cls) -> Dict[str, Any]:
        return {
            "fg_color"    : T.Color.BTN_SUBTLE,
            "hover_color" : T.Color.BTN_SUBTLE_HV,
            "text_color"  : T.Color.TEXT_MID,
            "border_width": 1,
            "border_color": T.Color.BORDER,
        }

    def _mini_btn(self, parent: ctk.CTkFrame, icon: str) -> ctk.CTkButton:
        sz = T.Size
        return ctk.CTkButton(
            parent,
            text          = icon,
            width         = UIScale.sm(sz.MINI_BTN_W),
            height        = UIScale.sm(sz.MINI_BTN_H),
            corner_radius = UIScale.sm(sz.MINI_BTN_R),
            font          = ("Segoe UI", UIScale.fm(T.Font.MINI_BTN_ICON)),
            fg_color      = "transparent",
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = T.Color.TEXT_MID,
            border_width  = 0,
        )

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        sz, sp = T.Size, T.Space

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, UIScale.pm(sp.HDR_PY)))
        header.grid_columnconfigure(1, weight=1)

        icon_box = self._card(
            header,
            width         = UIScale.sm(sz.ICON_BOX),
            height        = UIScale.sm(sz.ICON_BOX),
            corner_radius = UIScale.sm(sz.ICON_BOX_R),
        )
        icon_box.pack_propagate(False)
        icon_box.grid(row=0, column=0, padx=(0, UIScale.pm(sp.HDR_ICON_R)))

        self.icon_label = ctk.CTkLabel(
            icon_box,
            text       = "▶",
            font       = ("Segoe UI", UIScale.fm(T.Font.ICON_MAIN), "bold"),
            text_color = T.Color.MP3_ACTIVE,
        )
        self.icon_label.place(relx=0.5, rely=0.44, anchor="center")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            title_frame,
            text       = "Universal Downloader",
            font       = ("Segoe UI", UIScale.fm(T.Font.APP_TITLE), "bold"),
            text_color = T.Color.TEXT_BRIGHT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text       = "MP3  ·  MP4  ·  20+ sites  ·  Auto-retry",
            font       = ("Segoe UI", UIScale.fm(T.Font.APP_SUB)),
            text_color = T.Color.TEXT_DIM,
        ).pack(anchor="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        self.about_button = self._mini_btn(btn_frame, "💡")
        self.about_button.pack(side="right")

        def _about_enter(_):
            if self.about_button.cget("state") != "disabled":
                self.about_button.configure(
                    text_color="#fbbf24", fg_color=T.Color.BTN_SUBTLE_HV)

        def _about_leave(_):
            if self.about_button.cget("state") != "disabled":
                self.about_button.configure(
                    text_color=T.Color.TEXT_MID, fg_color="transparent")

        self.about_button.bind("<Enter>", _about_enter)
        self.about_button.bind("<Leave>", _about_leave)

        self.history_button = self._mini_btn(btn_frame, "📋")
        self.history_button.pack(side="right", padx=(0, UIScale.pm(sp.HDR_BTN_GAP)))

        def _history_enter(_):
            if self.history_button.cget("state") != "disabled":
                self.history_button.configure(
                    text_color=T.Color.HIST_HOVER, fg_color=T.Color.BTN_SUBTLE_HV)

        def _history_leave(_):
            if self.history_button.cget("state") != "disabled":
                self.history_button.configure(
                    text_color=T.Color.TEXT_MID, fg_color="transparent")

        self.history_button.bind("<Enter>", _history_enter)
        self.history_button.bind("<Leave>", _history_leave)

    def _build_separator(self, parent: ctk.CTkFrame) -> None:
        ctk.CTkFrame(
            parent,
            height   = UIScale.sm(T.Size.SEP_H),
            fg_color = T.Color.SEP,
        ).grid(row=1, column=0, sticky="ew", pady=(0, UIScale.pm(T.Space.SECTION_GAP)))

    def _build_url_card(self, parent: ctk.CTkFrame) -> None:
        sz, sp = T.Size, T.Space

        card = self._card(parent)
        card.grid(row=2, column=0, sticky="ew", pady=(0, UIScale.pm(sp.SECTION_GAP)))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        row_h   = UIScale.sm(sz.INPUT_ROW_H)
        entry_h = UIScale.sm(sz.INPUT_H)
        inset_y = max(0, UIScale.pm((sz.INPUT_ROW_H - sz.INPUT_H) // 2))
        row_py  = UIScale.pm(sp.CARD_ROW_PY)

        input_row = ctk.CTkFrame(
            card,
            fg_color      = T.Color.BG_INPUT,
            corner_radius = UIScale.sm(sz.INPUT_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
            height        = row_h,
        )
        input_row.grid(
            row=0, column=0, sticky="ew",
            padx=(UIScale.pm(sp.CARD_PX), UIScale.pm(sp.ADD_BTN_PX)),
            pady=row_py,
        )
        input_row.grid_propagate(False)
        input_row.grid_columnconfigure(1, weight=1)
        input_row.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            input_row,
            text       = "🔗",
            font       = ("Segoe UI", UIScale.fm(T.Font.URL_INPUT)),
            text_color = T.Color.TEXT_DIM,
            width      = UIScale.sm(sz.LINK_ICON_W),
        ).grid(row=0, column=0, padx=(UIScale.pm(sp.URL_ICON_PX), 0), pady=inset_y)

        self.url_entry = ctk.CTkEntry(
            input_row,
            placeholder_text       = (
                "https://www.youtube.com/ . . . . . . . . . . .  (Enter to add)"
            ),
            font                   = ("Segoe UI", UIScale.fm(T.Font.URL_INPUT)),
            fg_color               = "transparent",
            border_width           = 0,
            text_color             = T.Color.TEXT_BRIGHT,
            placeholder_text_color = T.Color.TEXT_DIM,
            height                 = entry_h,
        )
        self.url_entry.grid(
            row=0, column=1, sticky="ew",
            padx=(UIScale.pm(sp.URL_ENTRY_PX), 0),
            pady=inset_y,
        )

        self._clear_entry_btn = ctk.CTkButton(
            input_row,
            text          = "✕",
            width         = UIScale.sm(sz.CLR_BTN),
            height        = UIScale.sm(sz.CLR_BTN),
            fg_color      = "transparent",
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = T.Color.TEXT_DIM,
            corner_radius = UIScale.sm(sz.CLR_BTN_R),
        )
        self._clear_entry_btn.grid(
            row=0, column=2,
            padx=(0, UIScale.pm(sp.URL_ENTRY_R)),
            pady=inset_y,
        )

        btn_h     = UIScale.sm(sz.ADD_BTN_H)
        btn_pady  = max(0, (row_h - btn_h) // 2) if row_h > btn_h else 0
        add_frame = ctk.CTkFrame(
            card,
            fg_color = "transparent",
            width    = UIScale.sm(sz.ADD_BTN_W),
            height   = btn_h,
        )
        add_frame.grid_propagate(False)
        add_frame.grid(
            row=0, column=1,
            padx=(0, UIScale.pm(sp.CARD_PX)),
            pady=(row_py + btn_pady, row_py + btn_pady),
            sticky="e",
        )

        self.add_button = ctk.CTkButton(
            add_frame,
            text          = "Add",
            width         = UIScale.sm(sz.ADD_BTN_W),
            height        = btn_h,
            corner_radius = UIScale.sm(sz.ADD_BTN_R),
            fg_color      = T.Color.MP3_MAIN,
            hover_color   = T.Color.MP3_HOVER,
            text_color    = "#ffffff",
            font          = ("Segoe UI", UIScale.fm(T.Font.ADD_BTN), "bold"),
        )
        self.add_button.pack(fill="both", expand=True)

    def wire_clear_entry(self, command: Callable) -> None:
        self._clear_entry_btn.configure(command=command)

    def _build_mode_card(self, parent: ctk.CTkFrame) -> None:
        sz, sp = T.Size, T.Space

        card = self._card(parent)
        card.grid(row=3, column=0, sticky="ew", pady=(0, UIScale.pm(sp.SECTION_GAP)))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=UIScale.pm(sp.CARD_PX), pady=UIScale.pm(sp.CARD_PY))

        step_row = ctk.CTkFrame(
            inner, fg_color="transparent", height=UIScale.sm(sz.CLEAR_DONE_H))
        step_row.pack(fill="x")
        step_row.pack_propagate(False)
        StepIndicator(step_row, 1, "Choose download format").pack(side="left")

        ctk.CTkFrame(inner, fg_color="transparent",
                     height=UIScale.sm(sp.QUEUE_SPACER)).pack(fill="x")

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1), weight=1)

        self.mp3_button = ctk.CTkButton(
            grid,
            text          = "♪  MP3  ·  320 Kbps",
            height        = UIScale.sm(sz.MODE_BTN_H),
            corner_radius = UIScale.sm(sz.MODE_BTN_R),
            fg_color      = T.Color.MP3_MAIN,
            hover_color   = T.Color.MP3_HOVER,
            text_color    = "white",
            font          = ("Segoe UI", UIScale.fm(T.Font.MODE_BTN), "bold"),
        )
        self.mp3_button.grid(
            row=0, column=0, sticky="ew", padx=(0, UIScale.pm(sp.MODE_GAP)))

        self.mp4_button = ctk.CTkButton(
            grid,
            text          = "🎬  MP4  ·  Best quality",
            height        = UIScale.sm(sz.MODE_BTN_H),
            corner_radius = UIScale.sm(sz.MODE_BTN_R),
            fg_color      = T.Color.MODE_OFF,
            hover_color   = T.Color.MODE_OFF_HV,
            text_color    = T.Color.TEXT_DIM,
            border_width  = 1,
            border_color  = T.Color.BORDER,
            font          = ("Segoe UI", UIScale.fm(T.Font.MODE_BTN), "bold"),
        )
        self.mp4_button.grid(
            row=0, column=1, sticky="ew", padx=(UIScale.pm(sp.MODE_GAP), 0))

    def _build_queue_panel(self, parent: ctk.CTkFrame) -> None:
        sz, sp = T.Size, T.Space

        outer = self._card(parent)
        outer.grid(row=4, column=0, sticky="nsew", pady=(0, UIScale.pm(sp.SECTION_GAP)))
        outer.grid_rowconfigure(2, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.grid(
            row=0, column=0, sticky="ew",
            padx=UIScale.pm(sp.QUEUE_HDR_PX),
            pady=(UIScale.pm(sp.QUEUE_HDR_PY), 0),
        )
        hdr.grid_columnconfigure(0, weight=1)
        StepIndicator(hdr, 2, "Queue").grid(row=0, column=0, sticky="w")

        self.clear_done_button = ctk.CTkButton(
            hdr,
            text          = "Clear done",
            width         = UIScale.sm(sz.CLEAR_DONE_W),
            height        = UIScale.sm(sz.CLEAR_DONE_H),
            corner_radius = UIScale.sm(sz.CLEAR_DONE_R),
            font          = ("Segoe UI", UIScale.fm(T.Font.BTN_SEC), "bold"),
            **self._sec_btn_style(),
        )
        self.clear_done_button.grid(row=0, column=1, sticky="e")

        ctk.CTkFrame(
            outer, fg_color="transparent", height=UIScale.sm(sp.QUEUE_SPACER),
        ).grid(row=1, column=0, sticky="ew", padx=UIScale.pm(sp.QUEUE_PX))

        self.queue_scroll = ctk.CTkScrollableFrame(
            outer,
            fg_color      = T.Color.BG_INPUT,
            corner_radius = UIScale.sm(sz.QUEUE_R),
            border_width  = 1,
            border_color  = T.Color.BORDER,
        )
        self.queue_scroll.grid(
            row=2, column=0, sticky="nsew",
            padx=UIScale.pm(sp.QUEUE_PX),
            pady=(0, UIScale.pm(sp.QUEUE_PY_B)),
        )

        self.empty_label = ctk.CTkLabel(
            self.queue_scroll,
            text       = "Add links above to build your queue…",
            font       = ("Segoe UI", UIScale.fm(T.Font.EMPTY_LABEL)),
            text_color = T.Color.TEXT_DIM,
        )
        self.empty_label.pack(pady=UIScale.pm(sp.QUEUE_EMPTY))

    def _build_path_row(self, parent: ctk.CTkFrame, initial_path: str) -> None:
        sz, sp = T.Size, T.Space

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=5, column=0, sticky="ew", pady=(0, UIScale.pm(sp.PATH_PY)))
        row.grid_columnconfigure(0, weight=1)

        self.path_label = ctk.CTkLabel(
            row,
            text       = f"📍  {initial_path}",
            font       = ("Segoe UI", UIScale.fm(T.Font.PATH_LABEL)),
            text_color = T.Color.TEXT_DIM,
            anchor     = "w",
        )
        self.path_label.grid(row=0, column=0, sticky="ew")

        self.path_button = ctk.CTkButton(
            row,
            text          = "📁",
            width         = UIScale.sm(sz.PATH_BTN),
            height        = UIScale.sm(sz.PATH_BTN),
            corner_radius = UIScale.sm(sz.PATH_BTN_R),
            font          = ("Segoe UI", UIScale.fm(T.Font.ICON_BTN)),
            fg_color      = "transparent",
            hover_color   = T.Color.BTN_SUBTLE_HV,
            text_color    = T.Color.TEXT_MID,
            border_width  = 0,
        )
        self.path_button.grid(row=0, column=1, sticky="e")

    def _build_start_button(self, parent: ctk.CTkFrame) -> None:
        sz = T.Size
        self.download_button = ctk.CTkButton(
            parent,
            text          = "Start Queue",
            height        = UIScale.sm(sz.START_BTN_H),
            corner_radius = UIScale.sm(sz.START_BTN_R),
            fg_color      = T.Color.MP3_MAIN,
            hover_color   = T.Color.MP3_HOVER,
            text_color    = "#ffffff",
            font          = ("Segoe UI", UIScale.fm(T.Font.START_BTN), "bold"),
        )
        self.download_button.grid(row=6, column=0, sticky="ew")

    _LOCKABLE = (
        "url_entry", "add_button", "path_button",
        "mp3_button", "mp4_button",
        "history_button", "clear_done_button",
    )

    def set_locked(self, locked: bool) -> None:
        state = "disabled" if locked else "normal"
        for attr in self._LOCKABLE:
            widget = getattr(self, attr, None)
            if widget:
                widget.configure(state=state)


# ══════════════════════════════════════════════════════════════════════════════
#  §17  QUEUE CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class QueueController:
    def __init__(
        self,
        queue_manager  : QueueManager,
        tools          : ToolManager,
        max_retries    : int,
        history        : DownloadHistory,
        music_dir_func : Callable[[], str],
        video_dir_func : Callable[[], str],
        save_path_func : Callable[[], str],
        on_started     : Callable[[], None],
        on_finished    : Callable[[int, int, bool, Optional[DownloadTask]], None],
        on_progress    : Callable[[DownloadTask, float, str, str], None],
        on_status      : Callable[[DownloadTask, str], None],
        on_task_done   : Callable[[DownloadTask], None],
        show_dialog    : Callable[[str, str, str, Optional[str]], None],
    ) -> None:
        self._queue       = queue_manager
        self._tools       = tools
        self._max_retries = max_retries
        self._history     = history
        self._music_dir   = music_dir_func
        self._video_dir   = video_dir_func
        self._save_path   = save_path_func
        self._on_started  = on_started
        self._on_finished = on_finished
        self._on_progress = on_progress
        self._on_status   = on_status
        self._on_task_done= on_task_done
        self._show_dialog = show_dialog

        self._stop_event : threading.Event          = threading.Event()
        self._is_running : bool                     = False
        self._run_lock   : threading.Lock           = threading.Lock()
        self._worker     : Optional[DownloadWorker] = None

    @property
    def is_running(self) -> bool:
        with self._run_lock:
            return self._is_running

    def start(self) -> None:
        with self._run_lock:
            if self._is_running:
                return
            if self._tools.missing:
                return
            if not self._queue.has_pending():
                self._show_dialog(
                    "Nothing to download",
                    "Add at least one link to the queue first.",
                    "warning",
                    None,
                )
                return

            save_dir = self._save_path()
            if not check_disk_space(save_dir, MIN_FREE_SPACE_MB):
                free_mb = 0
                try:
                    t = save_dir
                    while t and not os.path.exists(t):
                        t = os.path.dirname(t)
                    free_mb = shutil.disk_usage(t).free // (1024 * 1024)
                except OSError:
                    pass
                self._show_dialog(
                    "Not enough storage",
                    f"Available: {free_mb} MB\nAt least {MIN_FREE_SPACE_MB} MB recommended.",
                    "warning",
                    None,
                )
                return

            self._stop_event.clear()
            self._is_running = True

        self._on_started()
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
        worker = self._worker
        if worker is not None:
            proc = worker._active_process
            if proc is not None:
                terminate_process(proc)

    def _loop(self) -> None:
        last_done_task : Optional[DownloadTask] = None

        while not self._stop_event.is_set():
            task = self._queue.next_pending()
            if task is None:
                break
            self._process(task)
            if task.status == TaskStatus.DONE:
                last_done_task = task

        tasks        = self._queue.all_tasks()
        done_count   = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        failed_count = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

        with self._run_lock:
            self._is_running = False

        self._on_finished(done_count, failed_count, self._stop_event.is_set(), last_done_task)

    def _process(self, task: DownloadTask) -> None:
        worker = DownloadWorker(
            task              = task,
            tools             = self._tools,
            max_retries       = self._max_retries,
            music_dir_func    = self._music_dir,
            video_dir_func    = self._video_dir,
            progress_callback = self._on_progress,
            status_callback   = self._on_status,
            is_stopped        = lambda: self._stop_event.is_set(),
        )
        self._worker  = worker
        success, msg  = worker.run()
        self._worker  = None

        if not success and msg == "Cancelled by user.":
            task.status = TaskStatus.PENDING
            task.speed  = ""
            task.eta    = ""
        else:
            self._history.add(task)

        self._on_task_done(task)


# ══════════════════════════════════════════════════════════════════════════════
#  §18  APPLICATION ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.attributes("-alpha", 0)
        self.title("Universal Downloader  🎵 MP3  🎬 MP4")
        if IS_WINDOWS and os.path.isfile(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        self._setup_window()
        UIScale.init(self)

        self._tools     = ToolManager(BASE_DATA_DIR)
        self._history   = DownloadHistory()
        self._queue     = QueueManager()
        self._mode      : str = "MP3"
        self._music_dir : str = DEFAULT_MUSIC_DIR
        self._video_dir : str = DEFAULT_VIDEO_DIR

        self._anim_id            : Optional[str] = None
        self._anim_dots          : int           = 0
        self._original_btn_color : str           = ""

        self._last_resize_width  : int           = 0
        self._resize_job         : Optional[str] = None

        self._ui = AppUIBuilder(self)
        self._ui.build(initial_save_path=self._save_path())
        self.bind("<Configure>", self._on_resize)

        self._ctrl = QueueController(
            queue_manager  = self._queue,
            tools          = self._tools,
            max_retries    = MAX_RETRIES,
            history        = self._history,
            music_dir_func = lambda: self._music_dir,
            video_dir_func = lambda: self._video_dir,
            save_path_func = self._save_path,
            on_started     = self._on_queue_started,
            on_finished    = self._on_queue_finished_thread,
            on_progress    = self._on_progress,
            on_status      = self._on_status,
            on_task_done   =  lambda _t: None,
            show_dialog    = self._show_dialog,
        )

        self._wire_handlers()
        self._apply_mode("MP3")

        # Auto-updater — created unconditionally but start() is a no-op when
        # ENABLE_AUTO_UPDATE is False. Must be initialised after _ui.build().
        self._updater = AutoUpdater(self, self._ui.main_frame)

        self.after(T.Anim.FADE_IN_MS, lambda: self.attributes("-alpha", 1))
        self.after(260, self._check_tools)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Window close ─────────────────────────────────────────────────────────

    def _on_close(self) -> None:
        if self._ctrl.is_running:
            self._ctrl.stop()
            self.after(100, self._check_close_ready)
        else:
            self.destroy()

    def _check_close_ready(self) -> None:
        if not self._ctrl.is_running:
            self.destroy()
        else:
            self.after(100, self._check_close_ready)

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.update_idletasks()
        sw, sh = get_logical_screen(self)
        w = min(max(T.Window.MIN_W, int(sw * T.Window.W_PCT)), int(sw * T.Window.MAX_W_PCT))
        h = min(max(T.Window.MIN_H, int(sh * T.Window.H_PCT)), int(sh * T.Window.MAX_H_PCT))
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.resizable(T.Window.RESIZABLE, T.Window.RESIZABLE)
        self.minsize(T.Window.MIN_W, T.Window.MIN_H)
        self.configure(fg_color=T.Color.BG_ROOT)

    # ── Handler wiring ────────────────────────────────────────────────────────

    def _wire_handlers(self) -> None:
        ui = self._ui

        add_handler = AddToQueueHandler(
            url_entry         = ui.url_entry,
            add_button        = ui.add_button,
            queue_manager     = self._queue,
            tools             = self._tools,
            current_mode_func = lambda: self._mode,
            on_tasks_added    = lambda _: self._sync_queue(),
            show_dialog_func  = lambda t, m, k: self._show_dialog(t, m, k, None),
            root              = self,
        )
        ui.add_button.configure(command=add_handler.execute)
        ui.url_entry.bind("<Return>", lambda _: add_handler.execute())

        ui.wire_clear_entry(ClearUrlEntryHandler(ui.url_entry).execute)
        ui.url_entry.bind("<Button-3>", PasteHandler(ui.url_entry, self).execute)

        mode_handler = SetModeHandler(
            mp3_button        = ui.mp3_button,
            mp4_button        = ui.mp4_button,
            icon_label        = ui.icon_label,
            add_button        = ui.add_button,
            download_button   = ui.download_button,
            path_label        = ui.path_label,
            get_save_path     = self._save_path,
            is_running        = lambda: self._ctrl.is_running,
            set_current_mode  = self._set_mode,
            update_path_label = lambda: ui.path_label.configure(
                text=f"📍  {self._save_path()}"
            ),
        )
        ui.mp3_button.configure(command=lambda: mode_handler.execute("MP3"))
        ui.mp4_button.configure(command=lambda: mode_handler.execute("MP4"))

        path_handler = ChangePathHandler(
            path_label       = ui.path_label,
            get_save_path    = self._save_path,
            is_running       = lambda: self._ctrl.is_running,
            root             = self,
            on_paths_changed = self._update_dirs,
        )
        ui.path_button.configure(command=path_handler.execute)

        start_stop = StartStopQueueHandler(
            download_button  = ui.download_button,
            queue_controller = self._ctrl,
            on_stop_callback = self._stop_anim,
        )
        ui.download_button.configure(command=start_stop.execute)

        ui.clear_done_button.configure(
            command=ClearDoneHandler(self._queue, self._sync_queue).execute)
        ui.history_button.configure(
            command=ShowHistoryHandler(self, self._history).execute)
        ui.about_button.configure(
            command=ShowAboutHandler(self).execute)

    # ── State helpers ─────────────────────────────────────────────────────────

    def _set_mode(self, mode: str) -> None:
        self._mode = mode

    def _save_path(self, mode: Optional[str] = None) -> str:
        m = mode or self._mode
        return self._music_dir if m == "MP3" else self._video_dir

    def _update_dirs(self, music: str, video: str) -> None:
        self._music_dir = music
        self._video_dir = video

    def _apply_mode(self, mode: str) -> None:
        style            = MODE_STYLES[mode]
        active, inactive = (
            (self._ui.mp3_button, self._ui.mp4_button) if mode == "MP3"
            else (self._ui.mp4_button, self._ui.mp3_button)
        )
        active.configure(
            fg_color=style.accent, hover_color=style.hover,
            text_color="#ffffff", border_width=0,
        )
        inactive.configure(
            fg_color=T.Color.MODE_OFF, hover_color=T.Color.MODE_OFF_HV,
            text_color=T.Color.TEXT_DIM, border_width=1,
            border_color=T.Color.BORDER,
        )
        self._ui.icon_label.configure(text_color=style.active)
        self._ui.add_button.configure(
            fg_color=style.accent, hover_color=style.hover, text_color="#ffffff")
        self._ui.download_button.configure(
            fg_color=style.accent, hover_color=style.hover, text_color="#ffffff")
        self._ui.path_label.configure(text=f"📍  {self._save_path()}")

    # ── Download-button animation ─────────────────────────────────────────────

    def _start_anim(self) -> None:
        self._anim_dots          = 0
        self._original_btn_color = self._ui.download_button.cget("text_color")
        self._tick_anim()
        self._ui.download_button.bind("<Enter>", self._anim_hover_enter)
        self._ui.download_button.bind("<Leave>", self._anim_hover_leave)

        self.update_idletasks()
        px, py = self.winfo_pointerxy()
        btn    = self._ui.download_button
        if (btn.winfo_rootx() <= px <= btn.winfo_rootx() + btn.winfo_width() and
                btn.winfo_rooty() <= py <= btn.winfo_rooty() + btn.winfo_height()):
            self._anim_hover_enter()

    def _stop_anim(self, reset_text: bool = True) -> None:
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        try:
            self._ui.download_button.unbind("<Enter>")
            self._ui.download_button.unbind("<Leave>")
        except Exception:
            pass
        if reset_text:
            self._update_start_label()

    def _tick_anim(self) -> None:
        dots   = "." * ((self._anim_dots % 4) + 1)
        spaces = " " * (4 - len(dots))
        self._ui.download_button.configure(text=f"Downloading{dots}{spaces}")
        self._anim_dots += 1
        self._anim_id = self.after(T.Anim.BTN_TICK_MS, self._tick_anim)

    def _anim_hover_enter(self, _event=None) -> None:
        if self._ctrl.is_running:
            self._ui.download_button.configure(text_color=T.Color.BTN_DANGER)

    def _anim_hover_leave(self, _event=None) -> None:
        if self._ctrl.is_running:
            self._ui.download_button.configure(text_color=self._original_btn_color)

    # ── Resize handler ────────────────────────────────────────────────────────

    def _on_resize(self, event=None) -> None:
        if event and event.widget != self:
            return
        new_w = self.winfo_width()
        if new_w == self._last_resize_width:
            return
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(80, self._do_resize, new_w)

    def _do_resize(self, new_w: int) -> None:
        self._resize_job        = None
        self._last_resize_width = new_w
        for child in self._ui.queue_scroll.winfo_children():
            if isinstance(child, QueueRow):
                child.refresh()

    # ── Queue display ─────────────────────────────────────────────────────────

    def _sync_queue(self) -> None:
        tasks = self._queue.all_tasks()

        for w in list(self._ui.queue_scroll.winfo_children()):
            if isinstance(w, QueueRow):
                w.destroy()

        for task in tasks:
            row = QueueRow(
                self._ui.queue_scroll,
                task,
                on_remove       = RemoveTaskHandler(task, self._queue, self._sync_queue).execute,
                is_running_func = lambda: self._ctrl.is_running,
            )
            row.pack(fill="x", pady=(0, T.Space.QUEUE_ROW_PY))

        for w in self._ui.queue_scroll.winfo_children():
            if isinstance(w, QueueRow):
                w.refresh()

        if not tasks:
            self._ui.empty_label.pack(pady=UIScale.pm(T.Space.QUEUE_EMPTY))
        else:
            try:
                self._ui.empty_label.pack_forget()
            except Exception:
                pass

        self._update_start_label()

    def _refresh_row(self, task: DownloadTask, sub_text: str) -> None:
        for w in self._ui.queue_scroll.winfo_children():
            if isinstance(w, QueueRow) and w.task is task:
                w.refresh(sub_text=sub_text)
                break

    def _update_start_label(self) -> None:
        if self._ctrl.is_running:
            return
        pending = sum(1 for t in self._queue.all_tasks() if t.status == TaskStatus.PENDING)
        self._ui.download_button.configure(
            text=f"Start Queue  ({pending})" if pending else "Start Queue"
        )

    # ── Queue lifecycle callbacks ─────────────────────────────────────────────

    def _on_queue_started(self) -> None:
        self._ui.set_locked(True)
        self._start_anim()

    def _on_queue_finished_thread(
        self,
        done           : int,
        failed         : int,
        stopped        : bool,
        last_done_task : Optional[DownloadTask] = None,
    ) -> None:
        self.after(0, self._on_queue_finished_main, done, failed, stopped, last_done_task)

    def _on_queue_finished_main(
        self,
        done           : int,
        failed         : int,
        stopped        : bool,
        last_done_task : Optional[DownloadTask] = None,
    ) -> None:
        self._ui.set_locked(False)
        self._apply_mode(self._mode)
        self._stop_anim(reset_text=True)
        style = MODE_STYLES[self._mode]
        self._ui.download_button.configure(
            fg_color=style.accent, hover_color=style.hover,
            text_color="white", state="normal",
        )
        self._sync_queue()
        if not stopped:
            self._show_completion_dialog(done, failed, last_done_task)

    def _show_completion_dialog(
        self,
        done           : int,
        failed         : int,
        last_done_task : Optional[DownloadTask] = None,
    ) -> None:
        if done and not failed:
            mode     = last_done_task.mode       if last_done_task else self._mode
            save_dir = (last_done_task.save_path
                        if (last_done_task and last_done_task.save_path)
                        else self._save_path())
            plural   = "s" if done > 1 else ""
            self._show_dialog(
                "Queue complete",
                f"All {done} download{plural} finished successfully!\n\nSaved in:\n{save_dir}",
                "success_mp3" if mode == "MP3" else "success_mp4",
                save_dir,
            )
        elif done and failed:
            self._show_dialog(
                "Queue finished with errors",
                f"{done} succeeded, {failed} failed.\nCheck the queue for details.",
                "warning",
                None,
            )
        elif failed:
            plural = "s" if failed > 1 else ""
            self._show_dialog(
                "All downloads failed",
                f"{failed} item{plural} could not be downloaded.\nCheck the queue for details.",
                "error",
                None,
            )

    # ── Progress / status callbacks ───────────────────────────────────────────

    def _on_progress(
        self,
        task  : DownloadTask,
        pct   : float,
        speed : str,
        eta   : str,
    ) -> None:
        def _update() -> None:
            task.percent = pct
            task.speed   = speed
            task.eta     = eta
            parts = []
            if speed:
                parts.append(f"↑ {speed}")
            if eta:
                parts.append(f"ETA {eta}")
            self._refresh_row(task, " · ".join(parts) or "Downloading…")
        self.after(0, _update)

    def _on_status(self, task: DownloadTask, message: str) -> None:
        self.after(0, self._refresh_row, task, message)

    def _show_dialog(
        self,
        title            : str,
        message          : str,
        kind             : str,
        open_folder_path : Optional[str] = None,
    ) -> None:
        ThemedDialog(
            self, title, message,
            kind             = kind,
            open_folder_path = open_folder_path,
        ).show()

    # ── Tool check on startup ─────────────────────────────────────────────────

    def _check_tools(self) -> None:
        missing = self._tools.missing
        if not missing:
            # Tools are present — safe to start the update check
            self._updater.start()
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Missing Tools")
        if IS_WINDOWS and os.path.isfile(ICON_PATH):
             self.after(200, lambda: dialog.iconbitmap(ICON_PATH) if dialog.winfo_exists() else None)

        sw, sh = get_logical_screen(dialog)
        w = min(max(UIScale.s(400), int(sw * 0.18)), int(sw * 0.44))
        h = min(max(UIScale.s(180), int(sh * 0.14)), int(sh * 0.24))
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.resizable(False, False)
        dialog.configure(fg_color=T.Color.BG_ROOT)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=(
                f"The following required tools are missing:\n\n"
                f"{', '.join(missing)}\n\nDownload them now?"
            ),
            font       = ("Segoe UI", UIScale.f(T.Font.DLG_MSG)),
            wraplength = UIScale.s(340),
            justify    = "center",
            text_color = T.Color.TEXT_MID,
        ).pack(pady=UIScale.p(20), padx=UIScale.p(20))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(pady=10)
        result = [False]

        def _yes() -> None:
            result[0] = True
            dialog.destroy()

        def _no() -> None:
            result[0] = False
            dialog.destroy()

        ctk.CTkButton(
            btn_row, text="Yes", command=_yes, width=80,
            fg_color      = T.Color.MP3_ACTIVE,
            hover_color   = T.Color.MP3_HOVER,
            corner_radius = UIScale.s(10),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_row, text="No", command=_no, width=80,
            fg_color      = T.Color.BTN_DANGER,
            corner_radius = UIScale.s(10),
        ).pack(side="left", padx=10)

        dialog.transient(self)
        dialog.wait_window()

        if not result[0]:
            self.after(0, self._exit_app, 0)
            return

        downloader = ToolDownloader(self, missing, self._tools)
        success, error_msg = downloader.show()
        self._tools.refresh()

        if success and not self._tools.missing:
            # Tools downloaded — start update check now
            self._updater.start()
            return

        still = ", ".join(self._tools.missing)
        self._show_dialog(
            "Tool download failed",
            error_msg or f"Missing: {still}",
            "error",
        )
        self.after(0, self._exit_app, 1)

    def _exit_app(self, code: int) -> None:
        try:
            self.destroy()
        except Exception:
            pass
        sys.exit(code)


# ══════════════════════════════════════════════════════════════════════════════
#  §19  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = App()
    app.mainloop()




