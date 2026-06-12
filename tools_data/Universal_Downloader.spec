# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
#  Universal_Downloader.spec
#  PyInstaller build specification — produces a single standalone .exe
#
#  Usage
#  -----
#      cd tools_data
#      pyinstaller Universal_Downloader.spec
#
#  Output: dist/Universal Downloader.exe
# =============================================================================

import json
import os
import sys

# ---------------------------------------------------------------------------
#  Version helpers
#  Read from version.json (one level above this spec file) so that the spec
#  never imports the main module and never loads tkinter at build time.
# ---------------------------------------------------------------------------

def _load_version_data() -> dict:
    """Return the parsed version.json dict, or an empty dict on failure."""
    spec_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    root_dir  = os.path.dirname(spec_dir)
    json_path = os.path.join(root_dir, "version.json")
    try:
        with open(json_path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _version_tuple(data: dict) -> tuple:
    """Return a (major, minor, patch) int-tuple from version data."""
    try:
        parts = data.get("version", "1.0.0").split(".")
        return tuple(int(p) for p in parts[:3])
    except Exception:
        return (1, 0, 0)


def _version_dot4(data: dict) -> str:
    """Return a ``major.minor.patch.build`` string from version data."""
    try:
        ver   = data.get("version", "1.0.0")
        build = int(data.get("build", 1))
        return f"{ver}.{build}"
    except Exception:
        return "1.0.0.1"


_vdata        = _load_version_data()
_version_3    = _version_tuple(_vdata)        # e.g. (1, 0, 0)
_version_str  = _version_dot4(_vdata)         # e.g. "1.0.0.1"
_publisher    = _vdata.get("publisher", "Bittar Tech Lab")
_app_name     = _vdata.get("app_name",  "Universal Downloader")

# ---------------------------------------------------------------------------
#  Path definitions
#  Expected layout:
#      <root>/
#      ├── version.json
#      └── tools_data/
#          ├── Universal_Downloader.spec   ← this file
#          ├── universal_downloader.py
#          ├── get_version.py
#          └── universal.ico
# ---------------------------------------------------------------------------

_spec_dir   = os.path.dirname(os.path.abspath(sys.argv[0]))
_script     = os.path.join(_spec_dir, "universal_downloader.py")
_icon       = os.path.join(_spec_dir, "universal.ico")

# ---------------------------------------------------------------------------
#  Analysis
# ---------------------------------------------------------------------------

a = Analysis(
    [_script],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle the entire tools_data folder so runtime resources
        # (icon, future assets) are available via sys._MEIPASS/tools_data/
        (_spec_dir, "tools_data"),
    ],
    hiddenimports=[
        # GUI
        "customtkinter",
        "tkinter",
        # Standard library modules that PyInstaller may miss
        "ctypes",
        "dataclasses",
        "enum",
        "hashlib",
        "json",
        "logging",
        "os",
        "platform",
        "re",
        "shutil",
        "subprocess",
        "threading",
        "time",
        "typing",
        "urllib.request",
        "webbrowser",
        "zipfile",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Keep the binary lean — strip test / dev dependencies
        "pytest",
        "unittest",
        "doctest",
        "pdb",
        "pip",
        "setuptools",
    ],
    noarchive=False,
    optimize=1,          # Strip docstrings from bytecode (safe for GUI apps)
)

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
#  EXE — single-file, windowless
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=_app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                       # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon if os.path.isfile(_icon) else None,
    onefile=True,
)

# ---------------------------------------------------------------------------
#  Windows version resource (embedded into the .exe PE header)
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    from PyInstaller.utils.win32 import versioninfo as _vi

    exe.version = _vi.VSVersionInfo(
        ffi=_vi.FixedFileInfo(
            filevers=_version_3 + (0,),
            prodvers=_version_3 + (0,),
            mask=0x3F,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0),
        ),
        kids=[
            _vi.StringFileInfo([
                _vi.StringTable(
                    "040904B0",
                    [
                        _vi.StringStruct("CompanyName",      _publisher),
                        _vi.StringStruct("FileDescription",  f"{_app_name} — MP3/MP4 downloader"),
                        _vi.StringStruct("FileVersion",      _version_str),
                        _vi.StringStruct("InternalName",     _app_name),
                        _vi.StringStruct("LegalCopyright",   f"© 2026 {_publisher}"),
                        _vi.StringStruct("OriginalFilename", f"{_app_name}.exe"),
                        _vi.StringStruct("ProductName",      _app_name),
                        _vi.StringStruct("ProductVersion",   _version_str),
                    ],
                )
            ]),
            _vi.VarFileInfo([_vi.VarStruct("Translation", [0x0409, 0x04B0])]),
        ],
    )

# No COLLECT block — single-file output goes directly to dist/
