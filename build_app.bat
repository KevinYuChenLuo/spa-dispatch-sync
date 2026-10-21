@echo off
echo ===================================================
echo Building Healing Place Dispatch Executable...
echo ===================================================

call .venv\Scripts\activate

pyinstaller --noconfirm --onedir --name "HealingPlaceDispatch" --icon "logo.ico" --collect-all streamlit --collect-all tinydb --add-data "main.py;." --add-data "theme.py;." --add-data "pages;pages" --add-data "logo.ico;." run_app.py

echo Generating Create_Desktop_Shortcut.bat inside dist folder...
(
echo @echo off
echo set "APP_DIR=%%~dp0"
echo set "TARGET_EXE=%%APP_DIR%%HealingPlaceDispatch.exe"
echo set "ICON_FILE=%%APP_DIR%%_internal\logo.ico"
echo.
echo powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Healing Place Dispatch.lnk')); $s.TargetPath = '%%TARGET_EXE%%'; $s.WorkingDirectory = '%%APP_DIR%%'; $s.IconLocation = '%%ICON_FILE%%'; $s.WindowStyle = 7; $s.Save()"
echo.
echo echo ========================================================
echo echo Success! "Healing Place Dispatch" shortcut with logo 
echo echo has been created on your Desktop!
echo echo ========================================================
echo pause
) > "dist\HealingPlaceDispatch\Create_Desktop_Shortcut.bat"

:: Remove any leftover test database before zipping for release
if exist "dist\HealingPlaceDispatch\spa_data.json" del "dist\HealingPlaceDispatch\spa_data.json"

echo Creating Release ZIP archive...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\HealingPlaceDispatch' -DestinationPath 'dist\HealingPlaceDispatch-Release.zip' -Force"

echo ===================================================
echo Done! Your updated app and ZIP file are ready in:
echo dist\HealingPlaceDispatch-Release.zip
echo ===================================================
pause