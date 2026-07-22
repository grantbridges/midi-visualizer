# -*- mode: python ; coding: utf-8 -*-

import sys
import platform

datas = [
    ("assets", "assets"),
]

binaries = []

if sys.platform == "win32":
    binaries += [
        ("third-party/ffmpeg/win32-x64/ffmpeg.exe", "bin"),
    ]
elif sys.platform == "darwin":
    arch = platform.machine()
    if arch == "arm64":
        binaries += [
            ("third-party/ffmpeg/darwin-arm64/ffmpeg", "bin"),
        ]
    elif arch == "x86_64":
        binaries += [
            ("third-party/ffmpeg/darwin-x64/ffmpeg", "bin"),
        ]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Illustri MIDI Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Illustri MIDI Studio',
)
app = BUNDLE(
    coll,
    name='Illustri MIDI Studio.app',
    icon=None,
    bundle_identifier=None,
)
