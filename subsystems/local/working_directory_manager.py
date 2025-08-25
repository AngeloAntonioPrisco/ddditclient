from pathlib import Path

# -------- CONFIGURATION --------
APP_NAME = "Dddit"

AUTH_DIR = Path.home() / "AppData" / "Local" / APP_NAME / "auth"

AUTH_DIR.mkdir(parents=True, exist_ok=True)

WORKING_DIRECTORY_FILE = AUTH_DIR / "working_directory.session"

# -------- WORKING DIRECTORY MANAGEMENT FUNCTIONS --------

def save_working_directory(path: str):
    with open(WORKING_DIRECTORY_FILE, "w", encoding="utf-8") as f:
        f.write(path)

def load_working_directory() -> Path :
    if WORKING_DIRECTORY_FILE.exists():
        with open(WORKING_DIRECTORY_FILE, "r", encoding="utf-8") as f:
            return Path(f.read().strip())
    return Path.home()

def clear_working_directory():
    if WORKING_DIRECTORY_FILE.exists():
        WORKING_DIRECTORY_FILE.unlink()
