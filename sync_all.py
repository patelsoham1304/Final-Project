"""Full Sync Script: Mirrors all modified files & folders from Desktop\\Python into patelsoham1304-automatic-telegram"""

import os
import shutil

SOURCE = r"C:\Users\LENOVO\Desktop\Python"
DESTINATIONS = [
    r"C:\Users\LENOVO\Desktop\Backup",
    r"C:\Backup\patelsoham1304-automatic-telegram",
    r"C:\Users\LENOVO\copilot-worktrees\Python\patelsoham1304-automatic-telegram",
]

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".vscode", ".idea"}
EXCLUDE_EXTS = {".pyc", ".tmp"}


def sync_all():
    for target in DESTINATIONS:
        if not os.path.exists(target):
            try:
                os.makedirs(target, exist_ok=True)
            except Exception:
                continue

        print(f"\n==================================================")
        print(f"[*] Syncing to: {target}")
        print(f"==================================================")

        copied = 0
        overwritten = 0

        for root, dirs, files in os.walk(SOURCE):
            # Filter unwanted folders
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

            rel_path = os.path.relpath(root, SOURCE)
            dest_root = target if rel_path == "." else os.path.join(target, rel_path)

            os.makedirs(dest_root, exist_ok=True)

            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue

                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_root, file)

                # Check if new or updated
                is_update = os.path.exists(dst_file)
                try:
                    shutil.copy2(src_file, dst_file)
                    if is_update:
                        overwritten += 1
                    else:
                        copied += 1
                except Exception as err:
                    print(f"  [!] Failed {file}: {err}")

        print(f"[SUCCESS] {target}:")
        print(f"   -> {overwritten} existing files updated/overwritten")
        print(f"   -> {copied} new files added")


if __name__ == "__main__":
    sync_all()
