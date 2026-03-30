@echo off
REM Build script pre Windows — vytvori WanderRemoteHost.exe
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set HOST_DIR=%PROJECT_DIR%\host
set VENV_DIR=%PROJECT_DIR%\venv_build

echo === Wander Remote Host — Windows build ===
echo Projekt: %PROJECT_DIR%
echo.

REM Kontrola Pythonu
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo CHYBA: python nie je nainstalovany alebo nie je v PATH
    exit /b 1
)

python --version
echo.

REM Vytvor venv
echo Vytvarim virtualny prostredie...
python -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

REM Instaluj zavislosti
echo Instalujem zavislosti...
pip install --upgrade pip -q
pip install -r "%HOST_DIR%\requirements-build.txt" -q

REM Vycisti predchadzajuci build
echo.
echo Cistim predchadzajuci build...
if exist "%HOST_DIR%\dist" rmdir /s /q "%HOST_DIR%\dist"
if exist "%HOST_DIR%\build" rmdir /s /q "%HOST_DIR%\build"

REM Spusti build
echo Spustam PyInstaller...
cd /d "%HOST_DIR%"
python build.py

REM Upratanie
echo.
echo Mazem virtualny prostredie...
call deactivate
rmdir /s /q "%VENV_DIR%"

echo.
echo === Build dokonceny ===
echo Vystup: %HOST_DIR%\dist\WanderRemoteHost.exe
