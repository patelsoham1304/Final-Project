"""Sync script to integrate all files and folders from backup into Desktop Python."""

import os
import shutil

# Source folder jaha backup files hain
SOURCE_DIR = r"C:\Backup\patelsoham1304-automatic-telegram"

# Destination jaha project integrate karna hai
DEST_DIR = r"C:\Users\LENOVO\Desktop\Python"

IGNORE_ITEMS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "sync.py",
}


def run_sync():
    if not os.path.exists(SOURCE_DIR):
        print(f"[!] Source backup path not found: {SOURCE_DIR}")
        return

    print(f"[*] Starting Sync...")
    print(f"    From: {SOURCE_DIR}")
    print(f"    To:   {DEST_DIR}\n")

    count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Ignore git aur cache folders
        dirs[:] = [d for d in dirs if d not in IGNORE_ITEMS and not d.startswith(".")]

        rel_path = os.path.relpath(root, SOURCE_DIR)
        target_root = DEST_DIR if rel_path == "." else os.path.join(DEST_DIR, rel_path)

        os.makedirs(target_root, exist_ok=True)

        for filename in files:
            if filename in IGNORE_ITEMS or filename.endswith(".pyc"):
                continue
            src_file = os.path.join(root, filename)
            dst_file = os.path.join(target_root, filename)
            try:
                shutil.copy2(src_file, dst_file)
                count += 1
            except Exception as e:
                print(f"Error copying {filename}: {e}")

    print(f"[SUCCESS] All {count} files and folders synced successfully into {DEST_DIR}!")


if __name__ == "__main__":
    run_sync()
