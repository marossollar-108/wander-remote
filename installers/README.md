# Wander Remote Host — Buildovanie

## Predpoklady

- Python 3.10+
- pip

## macOS

```bash
cd installers
chmod +x build-mac.sh
./build-mac.sh
```

Vystup: `host/dist/WanderRemoteHost.app`

Spustenie: Dvakrat kliknut na .app subor, alebo:

```bash
open host/dist/WanderRemoteHost.app
```

## Windows

```bat
cd installers
build-windows.bat
```

Vystup: `host\dist\WanderRemoteHost.exe`

Spustenie: Dvakrat kliknut na .exe subor.

## Linux

```bash
cd installers
chmod +x build-linux.sh
./build-linux.sh
```

Vystup: `host/dist/WanderRemoteHost`

Spustenie:

```bash
./host/dist/WanderRemoteHost
```

## Poznamky

- Build sa spusta vzdy z korenoveho adresara projektu (`wander-remote/`)
- Vsetky skripty vytvoria virtualny prostredie (`venv_build/`), nainstaluju zavislosti a spustia PyInstaller
- Virtualny prostredie sa po builde automaticky zmaze
- Na macOS sa vytvori .app bundle, na Windows .exe, na Linuxe nativny binarny subor
