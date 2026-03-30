#!/usr/bin/env bash
# Build script pre Linux — vytvori WanderRemoteHost binarku
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST_DIR="$PROJECT_DIR/host"
VENV_DIR="$PROJECT_DIR/venv_build"

echo "=== Wander Remote Host — Linux build ==="
echo "Projekt: $PROJECT_DIR"
echo ""

# Kontrola Pythonu
if ! command -v python3 &> /dev/null; then
    echo "CHYBA: python3 nie je nainstalovany"
    echo "Nainstalujte: sudo apt install python3 python3-venv python3-tk"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python: $PYTHON_VERSION"

# Kontrola tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "CHYBA: tkinter nie je nainstalovany"
    echo "Nainstalujte: sudo apt install python3-tk"
    exit 1
}

# Vytvor venv
echo ""
echo "Vytvarim virtualny prostredie..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Instaluj zavislosti
echo "Instalujem zavislosti..."
pip install --upgrade pip -q
pip install -r "$HOST_DIR/requirements-build.txt" -q

# Vycisti predchadzajuci build
echo ""
echo "Cistim predchadzajuci build..."
rm -rf "$HOST_DIR/dist" "$HOST_DIR/build"

# Spusti build
echo "Spustam PyInstaller..."
cd "$HOST_DIR"
python build.py

# Upratanie
echo ""
echo "Mazem virtualny prostredie..."
deactivate
rm -rf "$VENV_DIR"

echo ""
echo "=== Build dokonceny ==="
echo "Vystup: $HOST_DIR/dist/WanderRemoteHost"
