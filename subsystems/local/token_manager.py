from pathlib import Path

# -------- CONFIGURATION --------
APP_NAME = "Dddit"

AUTH_DIR = Path.home() / "AppData" / "Local" / APP_NAME / "auth"

AUTH_DIR.mkdir(parents=True, exist_ok=True)

TOKEN_FILE = AUTH_DIR / "session.token"

# -------- TOKEN MANAGEMENT FUNCTIONS --------

def save_token(token: str):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)

def load_token() -> str | None:
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def clear_token():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
