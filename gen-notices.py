#!/usr/bin/env python3
"""
Full pipeline:
  1. Parse PyInstaller's xref-<name>.html to find every module actually
     bundled into the frozen app.
  2. Map those to real PyPI distribution names via importlib.metadata
     (handles opencv-python -> cv2, pillow -> PIL, etc. automatically).
  3. Pull full license text/authors for just those bundled packages via
     pip-licenses.
  4. Assemble everything -- plus the FFmpeg (GPLv3) and Qt/PySide6 (LGPLv3)
     blocks -- into a single NOTICES.txt ready to ship inside the app.

USAGE:
    1. Build your app so build/<name>/xref-<name>.html exists.
    2. pip install pip-licenses --break-system-packages
    3. Download the following once and keep them in ./licenses/:
         - licenses/COPYING.GPLv3.txt   (https://www.gnu.org/licenses/gpl-3.0.txt)
         - licenses/COPYING.LGPLv3.txt  (https://www.gnu.org/licenses/lgpl-3.0.txt)
    4. python gen-notices.py

OUTPUT:
    - NOTICES.txt
"""

import re
import sys
import json
import subprocess
from datetime import date
from pathlib import Path
from importlib.metadata import packages_distributions
from common.constants import Const

# ---------------------------------------------------------------------------
# Config -- edit these if your FFmpeg build or paths ever change
# ---------------------------------------------------------------------------

LICENSES_DIR = Path("licenses")
GPLV3_TEXT_PATH = LICENSES_DIR / "COPYING.GPLv3.txt"
LGPLV3_TEXT_PATH = LICENSES_DIR / "COPYING.LGPLv3.txt"

FFMPEG_VERSION = "8.1.2"
FFMPEG_SOURCE_COMMIT = "FFmpeg/FFmpeg@38b88335f9"
FFMPEG_SOURCE_URL = "https://github.com/FFmpeg/FFmpeg/commit/38b88335f9"

XREF_PATH = f"build/{Const.APP_ALT_NAME}/xref-{Const.APP_ALT_NAME}.html"

# Distribution names that are all part of the same Qt/PySide6 LGPLv3 family --
# grouped so we don't repeat the full LGPLv3 text four times.
QT_FAMILY = {"pyside6", "pyside6-addons", "pyside6-essentials", "shiboken6"}

# ---------------------------------------------------------------------------
# Step 1-2: figure out what's actually bundled
# ---------------------------------------------------------------------------

def parse_xref_top_level_modules() -> set[str]:
    with open(XREF_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    names = re.findall(r'<a name="([^"]+)"></a>', content)
    return {n.strip("'").split(".")[0] for n in names}


def get_bundled_distributions(graph_modules: set[str]) -> set[str]:
    import_to_dist = packages_distributions()
    used = set()
    for mod in graph_modules:
        dists = import_to_dist.get(mod)
        if dists:
            used.update(dists)
    return used


def get_full_license_info() -> list[dict]:
    result = subprocess.run(
        ["pip-licenses", "--format=json", "--with-urls",
         "--with-license-file", "--with-notice-file", "--with-authors"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def norm(name: str) -> str:
    return name.lower().replace("_", "-")


# ---------------------------------------------------------------------------
# Step 3: assemble NOTICES.txt
# ---------------------------------------------------------------------------

def read_static_text(path: Path, label: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (f"[[ {label} text not found at {path} -- download it and place it there,\n"
            f"   then re-run this script. ]]\n")


def build_ffmpeg_section() -> str:
    gpl_text = read_static_text(GPLV3_TEXT_PATH, "GPLv3")
    return (
        "================================================================\n"
        "FFmpeg\n"
        "================================================================\n"
        f"This software uses FFmpeg version {FFMPEG_VERSION}, licensed under\n"
        "the GNU General Public License version 3 (GPLv3), due to this build\n"
        "being compiled with --enable-gpl and --enable-version3 (bundling\n"
        "libx264, libx265, and OpenSSL support).\n\n"
        f"Corresponding source for this exact build:\n"
        f"  {FFMPEG_SOURCE_URL}\n"
        f"  (commit {FFMPEG_SOURCE_COMMIT})\n\n"
        "Full license text:\n\n"
        f"{gpl_text}\n"
    )


def build_qt_section(packages: list[dict]) -> str:
    lgpl_text = read_static_text(LGPLV3_TEXT_PATH, "LGPLv3")
    names = ", ".join(sorted(p["Name"] for p in packages))
    versions = {p["Version"] for p in packages}
    version_str = versions.pop() if len(versions) == 1 else "/".join(sorted(versions))
    return (
        "================================================================\n"
        "Qt / PySide6\n"
        "================================================================\n"
        f"This software uses the following components ({names}), version\n"
        f"{version_str}, under the GNU Lesser General Public License version 3\n"
        "(LGPLv3). Qt is used via dynamically-loaded shared libraries, not\n"
        "statically linked. Source for Qt is available at:\n"
        "  https://code.qt.io/cgit/qt/\n\n"
        "Full license text:\n\n"
        f"{lgpl_text}\n"
    )


def build_package_section(pkg: dict) -> str:
    name = pkg["Name"]
    version = pkg.get("Version", "")
    license_name = pkg.get("License", "Unknown")
    url = pkg.get("URL", "")
    authors = pkg.get("Author") or pkg.get("Authors") or ""
    license_text = pkg.get("LicenseText") or ""

    header = (
        "----------------------------------------------------------------\n"
        f"{name} {version}\n"
        f"License: {license_name}\n"
        + (f"URL: {url}\n" if url else "")
        + (f"Author(s): {authors}\n" if authors else "")
        + "----------------------------------------------------------------\n"
    )

    if license_text and license_text != "UNKNOWN":
        body = license_text.strip() + "\n"
    else:
        body = (f"[[ Full license text not captured automatically. This package is\n"
                f"   under {license_name} -- verify at {url} if needed. ]]\n")

    return header + "\n" + body + "\n"


def main():
    graph_modules = parse_xref_top_level_modules()
    used_distributions = get_bundled_distributions(graph_modules)
    used_lower = {norm(d) for d in used_distributions}

    all_packages = get_full_license_info()
    bundled = [p for p in all_packages if norm(p["Name"]) in used_lower]

    # uncomment this to inspect bundled licenses
    #with open("bundled_licenses.json", "w") as f:
    #    json.dump(bundled, f, indent=2)
    #print(f"Wrote bundled_licenses.json ({len(bundled)} packages)")

    qt_packages = [p for p in bundled if norm(p["Name"]) in QT_FAMILY]
    other_packages = [p for p in bundled if norm(p["Name"]) not in QT_FAMILY]

    sections = []
    sections.append(
        f"{Const.APP_NAME} -- Third-Party Notices\n"
        f"Generated {date.today().isoformat()}\n\n"
        "This application includes the following third-party software.\n"
        "Each component's license terms are reproduced below.\n\n"
    )
    sections.append(build_ffmpeg_section())
    if qt_packages:
        sections.append(build_qt_section(qt_packages))
    for pkg in sorted(other_packages, key=lambda p: p["Name"].lower()):
        sections.append(build_package_section(pkg))

    notices_text = "\n".join(sections)
    Path("NOTICES.txt").write_text(notices_text, encoding="utf-8")
    print("Wrote NOTICES.txt")


if __name__ == "__main__":
    main()