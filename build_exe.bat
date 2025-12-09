@echo off
chcp 65001 >nul
title Build Folder Locker - Kelompok 1
color 0A

echo ========================================
echo     BUILD APLIKASI PENGUNCI FOLDER
echo            KELOMPOK 1
echo ========================================
echo.

echo 1. Checking files...
echo    Current folder: %CD%
echo.

echo 2. Looking for Python files in src\...
dir /b src\*.py

echo.
echo 3. Found main file: src\folder_locker.py
echo    Icon: src\assets\favicon.ico
echo.

if not exist "src\folder_locker.py" (
    echo ❌ ERROR: Main file not found!
    echo    Expected: src\folder_locker.py
    echo    Available Python files:
    dir /b src\*.py
    pause
    exit /b 1
)

if not exist "src\assets\favicon.ico" (
    echo ⚠️  WARNING: Icon not found, using default
    set USE_ICON=0
) else (
    echo ✓ Icon found
    set USE_ICON=1
)
echo.

echo 4. Installing PyInstaller if needed...
python -m pip install pyinstaller --quiet
echo ✓ PyInstaller ready
echo.

echo 5. Building executable...
echo    Please wait 1-2 minutes...
echo.

REM ===== BUILD COMMAND =====
if %USE_ICON%==1 (
    echo    Building WITH custom icon...
    pyinstaller --onefile ^
                --windowed ^
                --name "FolderLocker" ^
                --icon "src\assets\favicon.ico" ^
                --add-data "src\assets\favicon.ico;." ^
                --clean ^
                --noconsole ^
                "src\folder_locker.py"
) else (
    echo    Building WITHOUT custom icon...
    pyinstaller --onefile ^
                --windowed ^
                --name "FolderLocker" ^
                --clean ^
                --noconsole ^
                "src\folder_locker.py"
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ BUILD FAILED! Error: %errorlevel%
    echo.
    echo TIPS:
    echo 1. Run Command Prompt as Administrator
    echo 2. Try: pyinstaller --onefile src\folder_locker.py
    pause
    exit /b 1
)

echo.
echo ✅ BUILD SUCCESSFUL!
echo.

echo 6. Checking output...
if exist "dist\FolderLocker.exe" (
    for %%F in ("dist\FolderLocker.exe") do (
        echo ✓ File: dist\FolderLocker.exe
        echo ✓ Size: %%~zF bytes
    )
) else (
    echo ❌ ERROR: No executable created!
    echo    Check build\ folder for logs
    dir build\
    pause
    exit /b 1
)
echo.

echo 7. Creating shortcut...
echo @echo off > "dist\RUN_ME.bat"
echo echo Starting Folder Locker... >> "dist\RUN_ME.bat"
echo echo ========================= >> "dist\RUN_ME.bat"
echo start FolderLocker.exe >> "dist\RUN_ME.bat"
echo echo. >> "dist\RUN_ME.bat"
echo echo If the app doesn't open, double-click FolderLocker.exe directly >> "dist\RUN_ME.bat"
echo pause >> "dist\RUN_ME.bat"
echo ✓ Created: dist\RUN_ME.bat
echo.

echo ========================================
echo    BUILD COMPLETE! 🎉
echo ========================================
echo.
echo 📁 OUTPUT in dist\ folder:
echo    FolderLocker.exe  - Main application
echo    RUN_ME.bat        - Easy launcher
echo.
echo 🚀 TO RUN:
echo    1. Open dist\ folder
echo    2. Double-click RUN_ME.bat
echo    3. Or double-click FolderLocker.exe
echo.
echo 📦 TO SHARE:
echo    Zip the entire dist\ folder
echo    Send to others (no Python needed!)
echo.

echo Press any key to open dist folder...
pause >nul

if exist "dist\" (
    explorer "dist"
) else (
    echo ❌ dist folder not found!
    pause
)