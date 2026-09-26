# PyInstaller build script
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "Jarvis" main.py
Write-Output "Build complete in dist/Jarvis/"
