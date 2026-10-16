"""Sync all latest changes from Desktop Python into the worktree / backup."""

import os
import shutil

SOURCE_DIR = r"C:\Users\LENOVO\Desktop\Python"
TARGET_DIR = r"C:\Users\LENOVO\copilot-worktrees\Python\patelsoham1304-automatic-telegram"
BACKUP_DIR = r"C:\Backup\patelsoham1304-automatic-telegram"

IGNORE_ITEMS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "sync.py",
    "sync_back.py",
}


def sync_to(dest):
    if not os.path.exists(dest):
        return
    print(f"[*] Updating {dest}...")
    copied = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_ITEMS and not d.startswith(".")]
        rel_path = os.path.relpath(root, SOURCE_DIR)
        target_root = dest if rel_path == "." else os.path.join(dest, rel_path)
        os.makedirs(target_root, exist_ok=True)
        for f in files:
            if f in IGNORE_ITEMS or f.endswith(".pyc"):
                continue
            src = os.path.join(root, f)
            dst = os.path.join(target_root, f)
            try:
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                pass
    print(f"[SUCCESS] Updated {copied} files in {dest}!")


if __name__ == "__main__":
    sync_to(TARGET_DIR)
    sync_to(BACKUP_DIR)
