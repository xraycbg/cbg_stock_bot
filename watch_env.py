import os
import time
from dotenv import load_dotenv
from github_db import GitHubDB

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")

def get_last_mtime():
    try:
        return os.path.getmtime(ENV_FILE)
    except Exception:
        return 0

def sync_password():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    pwd = os.getenv("APP_PASSWORD")
    if not pwd:
        return
    try:
        db = GitHubDB()
        state, sha = db.get_state()
        if state.get("app_password") != pwd:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Detected .env change. Syncing APP_PASSWORD={pwd} to GitHub DB...")
            state["app_password"] = pwd
            success, _ = db.update_state(state, sha)
            if success:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully synced APP_PASSWORD={pwd} to GitHub DB!")
    except Exception as e:
        print(f"Error syncing password: {e}")

if __name__ == "__main__":
    print("Watching .env for changes in background...")
    last_mtime = 0
    while True:
        current_mtime = get_last_mtime()
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            sync_password()
        time.sleep(1)
