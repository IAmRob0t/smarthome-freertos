param(
    [switch]$InstallPyInstaller
)

$ErrorActionPreference = "Stop"

if ($InstallPyInstaller) {
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
}

python -m PyInstaller -F -w --name SmartHomeUDPGui ".\resource\udp_gui.py"

Write-Host "Build done. EXE path: .\dist\SmartHomeUDPGui.exe" -ForegroundColor Green

