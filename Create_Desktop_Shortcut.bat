@echo off
set "APP_DIR=%~dp0"
set "TARGET_EXE=%APP_DIR%HealingPlaceDispatch.exe"
set "ICON_FILE=%APP_DIR%_internal\logo.ico"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Healing Place Dispatch.lnk')); $s.TargetPath = '%TARGET_EXE%'; $s.WorkingDirectory = '%APP_DIR%'; $s.IconLocation = '%ICON_FILE%'; $s.WindowStyle = 7; $s.Save()"

echo ========================================================
echo Success! "Healing Place Dispatch" shortcut with logo 
echo has been created on your Desktop!
echo ========================================================
pause