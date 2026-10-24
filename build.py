import os
import sys
import subprocess

def main():
    print("Starting automated PyInstaller build...")
    
    # Windows uses ';' and macOS uses ':' for path separators in --add-data
    sep = ";" if sys.platform.startswith("win") else ":"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--name", "HealingPlaceDispatch",
        "--icon", "logo.ico",
        "--collect-all", "streamlit",
        "--collect-all", "tinydb",
        f"--add-data=main.py{sep}.",
        f"--add-data=theme.py{sep}.",
        f"--add-data=pages{sep}pages",
        f"--add-data=logo.ico{sep}.",
        "run_app.py"
    ]
    
    subprocess.run(cmd, check=True)
    
    # Remove any test database before packaging
    target_dir = os.path.join("dist", "HealingPlaceDispatch")
    data_file = os.path.join(target_dir, "spa_data.json")
    if os.path.exists(data_file):
        os.remove(data_file)
        
    # Generate Windows shortcut script if building on Windows
    if sys.platform.startswith("win"):
        shortcut_script = os.path.join(target_dir, "Create_Desktop_Shortcut.bat")
        with open(shortcut_script, "w", encoding="utf-8") as f:
            f.write("""@echo off
set "APP_DIR=%~dp0"
set "TARGET_EXE=%APP_DIR%HealingPlaceDispatch.exe"
set "ICON_FILE=%APP_DIR%_internal\\logo.ico"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Healing Place Dispatch.lnk')); $s.TargetPath = '%TARGET_EXE%'; $s.WorkingDirectory = '%APP_DIR%'; $s.IconLocation = '%ICON_FILE%'; $s.WindowStyle = 7; $s.Save()"

echo ========================================================
echo Success! "Healing Place Dispatch" shortcut with logo 
echo has been created on your Desktop!
echo ========================================================
pause
""")
    
    print("Build completed successfully!")

if __name__ == "__main__":
    main()