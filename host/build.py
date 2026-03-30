"""Build script pre PyInstaller — vytvori standalone executable."""

import platform
import subprocess
import sys
from pathlib import Path

HOST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = HOST_DIR.parent
SHARED_DIR = PROJECT_DIR / "shared"
SPEC_FILE = HOST_DIR / "build.spec"

APP_NAME = "WanderRemoteHost"


def get_platform():
    """Zisti aktualnu platformu."""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "win"
    else:
        return "linux"


def build():
    """Spusti PyInstaller build."""
    plat = get_platform()
    print(f"Platforma: {plat}")
    print(f"Projekt: {PROJECT_DIR}")
    print(f"Shared: {SHARED_DIR}")
    print()

    # Pouzi spec subor ak existuje
    if SPEC_FILE.exists():
        print(f"Pouzivam spec subor: {SPEC_FILE}")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(SPEC_FILE),
        ]
    else:
        print("Spec subor nenajdeny, pouzivam prikazovy riadok")
        separator = ";" if plat == "win" else ":"

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--name", APP_NAME,
            "--distpath", str(HOST_DIR / "dist"),
            "--workpath", str(HOST_DIR / "build"),
            "--specpath", str(HOST_DIR),
            # Pridaj shared modul
            "--add-data", f"{SHARED_DIR}{separator}shared",
            # Pridaj config
            "--add-data", f"{HOST_DIR / 'config.py'}{separator}.",
            # Hidden imports
            "--hidden-import", "websockets",
            "--hidden-import", "mss",
            "--hidden-import", "PIL",
            "--hidden-import", "pyautogui",
            "--hidden-import", "numpy",
            "--hidden-import", "shared.protocol",
        ]

        if plat == "mac":
            cmd.extend([
                "--windowed",
                "--osx-bundle-identifier", "com.wanderhub.remotehost",
            ])
        elif plat == "win":
            # --windowed skryje konzolu na Windows
            cmd.append("--windowed")

        cmd.append(str(HOST_DIR / "host_gui.py"))

    print(f"Spustam: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(HOST_DIR))

    if result.returncode == 0:
        print()
        print("Build uspesny!")
        dist = HOST_DIR / "dist"
        if plat == "mac":
            print(f"  Vystup: {dist / (APP_NAME + '.app')}")
        elif plat == "win":
            print(f"  Vystup: {dist / (APP_NAME + '.exe')}")
        else:
            print(f"  Vystup: {dist / APP_NAME}")
    else:
        print()
        print(f"Build zlyhal s kodom {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
