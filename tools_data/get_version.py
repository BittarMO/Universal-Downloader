# -*- coding: utf-8 -*-
"""
get_version.py
~~~~~~~~~~~~~~
Reads APP_VERSION from universal_downloader.py using plain-text regex.

This module intentionally avoids importing the main application module so
that tkinter and customtkinter are never loaded at PyInstaller build time.

Expected layout
---------------
    <project>/
    └── tools_data/
        ├── universal_downloader.py   ← version source
        └── get_version.py            ← this file
"""

from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

_VERSION_PATTERN = re.compile(
    r'^\s*APP_VERSION\s*(?::\s*str\s*)?\=\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

_FALLBACK_VERSION = "1.0.0"


def _read_app_version() -> str:
    """
    Parse APP_VERSION from universal_downloader.py without importing it.

    Returns
    -------
    str
        Version string (e.g. ``"1.2.3"``), or ``"1.0.0"`` as a safe fallback
        if the file is missing or the assignment cannot be found.
    """
    src_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "universal_downloader.py",
    )

    try:
        with open(src_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                match = _VERSION_PATTERN.match(line)
                if match:
                    return match.group(1).strip()
    except OSError:
        pass

    return _FALLBACK_VERSION


# ---------------------------------------------------------------------------
#  Module-level constant — resolved once at import time
# ---------------------------------------------------------------------------

APP_VERSION: str = _read_app_version()


# ---------------------------------------------------------------------------
#  Public API
# ---------------------------------------------------------------------------

def get_version_string() -> str:
    """Return the raw version string, e.g. ``"1.2.3"``."""
    return APP_VERSION


def get_version_tuple() -> tuple[int, ...]:
    """
    Return the version as a 4-element integer tuple.

    Examples
    --------
    >>> get_version_tuple()
    (1, 2, 3, 0)
    """
    parts = [int(x) for x in APP_VERSION.split(".") if x.isdigit()]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def get_version_dot4() -> str:
    """
    Return a 4-component version string for Windows ``FileVersion`` metadata.

    Examples
    --------
    >>> get_version_dot4()
    '1.2.3.0'
    """
    major, minor, patch, build = get_version_tuple()
    return f"{major}.{minor}.{patch}.{build}"


# ---------------------------------------------------------------------------
#  Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"APP_VERSION : {get_version_string()}")
    print(f"Tuple       : {get_version_tuple()}")
    print(f"4-part      : {get_version_dot4()}")
