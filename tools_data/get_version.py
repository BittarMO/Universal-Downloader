# -*- coding: utf-8 -*-
"""
get_version.py
Reads APP_VERSION from universal_downloader.py as plain text (regex).
No import of the main module — avoids tkinter/customtkinter loading at build time.

Assumes:
    - This file (get_version.py) is inside the same folder as universal_downloader.py
    - Typical path: .../Universal Downloader/tools_data/get_version.py
"""

import os
import re


# ── Locate universal_downloader.py ───────────────────────────────────────────
#   Layout (new structure):
#       .../Universal Downloader/tools_data/get_version.py      ← __file__
#       .../Universal Downloader/tools_data/universal_downloader.py   ← target
# ─────────────────────────────────────────────────────────────────────────────

def _read_app_version() -> str:
    """
    Open universal_downloader.py from the same directory and extract the value of
    APP_VERSION without executing / importing the module.
    Falls back to '1.0.0' if the file is not found or the line is missing.
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))        # .../tools_data
    src_path = os.path.join(this_dir, "universal_downloader.py")

    pattern = re.compile(
        r'^\s*APP_VERSION\s*(?::\s*str\s*)?\=\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    try:
        with open(src_path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = pattern.match(line)
                if m:
                    return m.group(1).strip()
    except OSError:
        pass

    return "1.0.0"


APP_VERSION: str = _read_app_version()


# ── Public helpers ────────────────────────────────────────────────────────────

def get_version_tuple() -> tuple:
    """Return version as a 4-element integer tuple, e.g. (1, 0, 0, 0)."""
    parts = [int(x) for x in APP_VERSION.split(".") if x.isdigit()]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def get_version_string() -> str:
    """Return the raw version string, e.g. '1.0.0'."""
    return APP_VERSION


def get_version_dot_4() -> str:
    """Return a 4-component version string, e.g. '1.0.0.0'."""
    t = get_version_tuple()
    return f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"


# ── Quick self-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"APP_VERSION : {APP_VERSION}")
    print(f"Tuple       : {get_version_tuple()}")
    print(f"4-part      : {get_version_dot_4()}")