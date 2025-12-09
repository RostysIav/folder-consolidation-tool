#!/usr/bin/env python3
"""
Step 1: Empty Folder Cleanup Script
====================================
This script removes all empty folders (folders with no files at the end of the tree)
from your source folders BEFORE consolidation.

Run this first to clean up, then run the consolidation.
"""

import os
from pathlib import Path
from datetime import datetime

# Destination folder (where everything consolidates)
MASTER_FOLDER = r"C:\Users\YourUsername\Documents\master"

# Source folders to consolidate (add your paths here)
SOURCE_FOLDERS = [
    # Example paths - REPLACE WITH YOUR ACTUAL PATHS:
    r"C:\Users\YourUsername\Documents",
    r"C:\Users\YourUsername\Documents",
    r"C:\Users\YourUsername\Documents",
    # Add more paths as needed...
]

LOG_FILE = "empty_folders_cleanup_log.txt"
# =========================


class EmptyFolderCleaner:
    def __init__(self, log_file="cleanup_log.txt"):
        self.log_file = Path(log_file)
        self.stats = {
            'empty_folders_deleted': 0,
            'errors': 0
        }

    def log(self, message, print_also=True):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(log_message + "\n")
        if print_also:
            print(log_message)

    def is_folder_empty(self, folder_path):
        """
        Check if a folder is truly empty (no files anywhere in the tree).
        Returns True if empty, False if it contains at least one file.
        """
        folder_path = Path(folder_path)

        try:
            # Check all items recursively
            for item in folder_path.rglob('*'):
                if item.is_file():
                    return False  # Found a file, not empty
            return True  # No files found, it's empty
        except Exception as e:
            self.log(f"ERROR checking {folder_path}: {e}", True)
            return False

    def remove_empty_folders(self, folder_path):
        """
        Recursively remove empty folders.
        Works bottom-up (deepest folders first).
        """
        folder_path = Path(folder_path)

        if not folder_path.exists():
            self.log(f"ERROR: Path does not exist: {folder_path}", True)
            return

        try:
            # Get all subdirectories, sorted by depth (deepest first)
            all_dirs = sorted(
                [d for d in folder_path.rglob('*') if d.is_dir()],
                key=lambda p: len(p.parts),
                reverse=True
            )

            for directory in all_dirs:
                try:
                    # Check if directory is empty (no files inside)
                    if self.is_folder_empty(directory):
                        self.log(f"DELETING EMPTY: {directory}", True)
                        directory.rmdir()  # Remove empty directory
                        self.stats['empty_folders_deleted'] += 1
                except Exception as e:
                    self.log(f"ERROR deleting {directory}: {e}", False)
                    self.stats['errors'] += 1

        except Exception as e:
            self.log(f"ERROR processing {folder_path}: {e}", True)
            self.stats['errors'] += 1

    def clean_sources(self, source_folders):
        self.log("=" * 60, True)
        self.log("EMPTY FOLDER CLEANUP STARTED", True)
        self.log("=" * 60, True)

        for i, source in enumerate(source_folders, 1):
            source_path = Path(source)
            self.log(f"\n[{i}/{len(source_folders)}] Cleaning: {source_path}", True)

            if not source_path.exists():
                self.log(f"ERROR: Source not found: {source_path}", True)
                continue

            self.remove_empty_folders(source_path)

        self.log("\n" + "=" * 60, True)
        self.log("CLEANUP COMPLETE", True)
        self.log("=" * 60, True)
        self.print_statistics()

    def print_statistics(self):
        self.log("\nSTATISTICS:", True)
        self.log(f"  Empty Folders Deleted: {self.stats['empty_folders_deleted']}", True)
        self.log(f"  Errors:                {self.stats['errors']}", True)
        self.log(f"\nLog saved to: {self.log_file}", True)


def main():
    print("\n" + "=" * 60)
    print("EMPTY FOLDER CLEANUP TOOL")
    print("=" * 60)
    print("\nThis will DELETE all empty folders from your source folders.")
    print("Empty = No files anywhere in the folder tree.\n")

    if not SOURCE_FOLDERS:
        print("ERROR: Please edit SOURCE_FOLDERS in the script!")
        return

    print("Source folders to clean:")
    for i, folder in enumerate(SOURCE_FOLDERS, 1):
        print(f"  {i}. {folder}")

    confirm = input("\nProceed with cleanup? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    cleaner = EmptyFolderCleaner(LOG_FILE)
    cleaner.clean_sources(SOURCE_FOLDERS)

    print("\n✅ Cleanup complete! Check the log file for details.")


if __name__ == "__main__":
    main()
