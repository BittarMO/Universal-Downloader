# -*- mode: python ; coding: utf-8 -*-

import json
import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
#  Helper functions to read version from version.json (now one level up)
# ─────────────────────────────────────────────────────────────────────────────

def _get_version_tuple():
    """
    Return (major, minor, patch) from version.json.
    Assumes version.json is in the parent folder of tools_data.
    """
    try:
        # This spec file is in: .../Universal Downloader/tools_data/
        # So we go up one level to reach the root folder containing version.json
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
        json_path = os.path.join(base_dir, "version.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ver_str = data.get("version", "1.0.0")
        parts = ver_str.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        return (1, 0, 0)

def _get_version_dot_4():
    """
    Return version string like '1.0.0.1' (version.build) from version.json.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
        json_path = os.path.join(base_dir, "version.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ver_str = data.get("version", "1.0.0")
        build = data.get("build", 1)
        return f"{ver_str}.{build}"
    except Exception:
        return "1.0.0.1"

# Get version numbers
version_tuple = _get_version_tuple()
version_dot_4 = _get_version_dot_4()

# ─────────────────────────────────────────────────────────────────────────────
#  Path definitions (new structure: tools_data at same level as spec)
# ─────────────────────────────────────────────────────────────────────────────

spec_file_path = os.path.abspath(sys.argv[0])
tools_dir = os.path.dirname(spec_file_path)               # .../Universal Downloader/tools_data/
root_dir = os.path.dirname(tools_dir)                     # .../Universal Downloader/

# Main script is now inside tools_data
script_path = os.path.join(tools_dir, "universal_downloader.py")
# Icon
icon_path = os.path.join(tools_dir, "universal.ico")
# Data directory (tools_data itself) – will be copied as "tools_data" inside the exe
tools_data_dir = tools_dir

# ─────────────────────────────────────────────────────────────────────────────
#  PyInstaller Analysis
# ─────────────────────────────────────────────────────────────────────────────

a = Analysis(
    [script_path],
    pathex=[],
    binaries=[],
    datas=[
        # Include all files from tools_data (e.g., universal.ico, and future binaries)
        # Destination inside the frozen app will be "tools_data"
        (tools_data_dir, "tools_data"),
    ],
    hiddenimports=[
        "customtkinter",
        "tkinter",
        "logging",
        "os",
        "platform",
        "re",
        "shutil",
        "subprocess",
        "threading",
        "time",
        "urllib.request",
        "webbrowser",
        "zipfile",
        "dataclasses",
        "enum",
        "typing",
        "json",
        "hashlib",
        "ctypes",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Universal Downloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
)

# ─────────────────────────────────────────────────────────────────────────────
#  Version information for Windows
# ─────────────────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    from PyInstaller.utils.windows import versioninfo

    vs_version = versioninfo.VSVersionInfo(
        ffi=versioninfo.FixedFileInfo(
            filevers=version_tuple + (0,),
            prodvers=version_tuple + (0,),
            mask=0x3f,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0),
        ),
        kids=[
            versioninfo.StringFileInfo(
                [
                    versioninfo.StringTable(
                        u"040904B0",
                        [
                            versioninfo.StringStruct(u"CompanyName", u"Bittar Tech Lab"),
                            versioninfo.StringStruct(u"FileDescription", u"Universal Downloader – MP3/MP4 downloader"),
                            versioninfo.StringStruct(u"FileVersion", version_dot_4),
                            versioninfo.StringStruct(u"InternalName", u"Universal Downloader"),
                            versioninfo.StringStruct(u"LegalCopyright", u"© 2026 Bittar Tech Lab"),
                            versioninfo.StringStruct(u"OriginalFilename", u"Universal Downloader.exe"),
                            versioninfo.StringStruct(u"ProductName", u"Universal Downloader"),
                            versioninfo.StringStruct(u"ProductVersion", version_dot_4),
                        ],
                    )
                ]
            ),
            versioninfo.VarFileInfo([versioninfo.VarStruct(u"Translation", [0x0409, 0x04B0])]),
        ],
    )
    exe.version = vs_version

# COLLECT (for one-folder mode, kept for compatibility)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Universal Downloader",
)