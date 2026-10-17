import os
import sys
import streamlit.web.cli as stcli

def get_app_dir():
    """Returns the folder where the .exe lives (so spa_data.json saves permanently)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def get_bundled_dir():
    """Returns the internal folder where PyInstaller unpacks main.py, theme.py, and pages/."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    app_dir = get_app_dir()
    bundled_dir = get_bundled_dir()

    # Ensure spa_data.json is read/written in the permanent .exe folder
    os.chdir(app_dir)

    # Ensure Python can find theme.py when main.py or pages/staff.py imports it
    if bundled_dir not in sys.path:
        sys.path.insert(0, bundled_dir)

    main_script = os.path.join(bundled_dir, "main.py")

    sys.argv = [
        "streamlit",
        "run",
        main_script,
        "--global.developmentMode=false",
        "--server.headless=false",
    ]
    sys.exit(stcli.main())