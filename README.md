# MIDI Visualizer

I'll update this when I have something interesting!

## Dev Setup

### Pre-Reqs

- [Python](https://www.python.org/downloads/release/python-3146/) (3.14.6+)
- [FFmpeg](https://www.ffmpeg.org/) (8.1.2+)
  - _(Mac)_ Run `brew install ffmpeg`
  - _(Windows)_ Run `winget install ffmpeg`
- [VSCode](https://code.visualstudio.com/) (or your favorite code editor)

### Initial Setup

- Run `python -m venv .venv` to start up virtual environment. Activate with:
  - _(Mac)_ Run `source ./.venv/bin/activate`
  - _(Windows)_ Run `./.venv/Scripts/activate.bat`
- Run `python -m pip install -r ./requirements.txt` to install dependencies
- _(VSCode)_ Run Debug launch task to start app in debug mode

### Requirements Generation

When package dependencies are changed, run `python -m pigar generate --auto-select` to generate fresh requirements.txt. Enter "n" for the "Try to search them on PyPI for further analysis?" prompt.

## Build

1. Ensure you have `pyinstaller` (at least version 6.21.0) installed
   - `python -m pip install pyinstaller`
1. Run `sh ./build.sh` to generate build artifacts under `/dist`
