# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec pre WanderRemoteHost."""

import platform
from pathlib import Path

HOST_DIR = Path(SPECPATH)
PROJECT_DIR = HOST_DIR.parent
SHARED_DIR = PROJECT_DIR / "shared"

block_cipher = None
system = platform.system().lower()

a = Analysis(
    [str(HOST_DIR / "host_gui.py")],
    pathex=[str(HOST_DIR), str(PROJECT_DIR)],
    binaries=[],
    datas=[
        (str(SHARED_DIR), "shared"),
        (str(HOST_DIR / "config.py"), "."),
    ],
    hiddenimports=[
        "websockets",
        "mss",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "pyautogui",
        "numpy",
        "shared.protocol",
        "tkinter",
        "tkinter.ttk",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="WanderRemoteHost",
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
)

# macOS .app bundle
if system == "darwin":
    app = BUNDLE(
        exe,
        name="WanderRemoteHost.app",
        icon=None,
        bundle_identifier="com.wanderhub.remotehost",
        info_plist={
            "CFBundleName": "WanderRemoteHost",
            "CFBundleDisplayName": "Wander Remote Host",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
