"""Backup sync script: Copies all updated project files from Desktop\\Python to C:\\Backup\\patelsoham1304-automatic-telegram"""

import os
import shutil

SOURCE_DIR = r"C:\Users\LENOVO\Desktop\Python"
DEST_DIR = r"C:\Backup\patelsoham1304-automatic-telegram"

IGNORE_ITEMS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "backup_to_target.py",
}


def backup_project():
    if not os.path.exists(SOURCE_DIR):
        print(f"[!] Source directory not found: {SOURCE_DIR}")
        return

    os.makedirs(DEST_DIR, exist_ok=True)
    print(f"[*] Copying files...")
    print(f"    From: {SOURCE_DIR}")
    print(f"    To:   {DEST_DIR}\n")

    count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_ITEMS and not d.startswith(".")]

        rel_path = os.path.relpath(root, SOURCE_DIR)
        target_root = DEST_DIR if rel_path == "." else os.path.join(DEST_DIR, rel_path)
        os.makedirs(target_root, exist_ok=True)

        for filename in files:
            if filename in IGNORE_ITEMS or filename.endswith(".pyc") or filename.endswith(".tmp"):
                continue
            src_file = os.path.join(root, filename)
            dst_file = os.path.join(target_root, filename)
            try:
                shutil.copy2(src_file, dst_file)
                count += 1
            except Exception as e:
                print(f"Error copying {filename}: {e}")

    print(f"[SUCCESS] {count} files backed up to {DEST_DIR}!")


if __name__ == "__main__":
    backup_project()
