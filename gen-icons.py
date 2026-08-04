"""
Helper script to generate a Windows .ico and a macOS .icns from the 
single 1024x1024 at assets/illustri-icon.png, writing both into assets/icons/.

Must be run on a Mac for the 'iconutil' utility.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

# macOS .iconset requires these exact filenames/sizes.
ICNS_SIZES = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]

# Standard multi-resolution set to embed in the Windows .ico.
ICO_SIZES = [16, 32, 48, 256]

def generate_ico(master: Image.Image, output_path: Path) -> None:
    master.save(output_path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"Created {output_path}")

def generate_icns(master: Image.Image, output_path: Path) -> None:
    if shutil.which("iconutil") is None:
        print(
            "WARNING: 'iconutil' not found (this only ships with macOS). "
            "Skipping .icns generation.",
            file=sys.stderr,
        )
        return

    with tempfile.TemporaryDirectory() as tmp:
        iconset_dir = Path(tmp) / "Icon.iconset"
        iconset_dir.mkdir()

        for size, filename in ICNS_SIZES:
            resized = master.resize((size, size), Image.LANCZOS)
            resized.save(iconset_dir / filename)

        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
            check=True,
        )
    print(f"Created {output_path}")

def main() -> None:
    master_file = Path("assets/illustri-icon.png")
    output_dir = Path("assets/icons")

    master = Image.open(master_file).convert("RGBA")

    generate_ico(master, output_dir / f"illustri.ico")
    generate_icns(master, output_dir / f"illustri.icns")

if __name__ == "__main__":
    main()