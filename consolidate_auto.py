#!/usr/bin/env python3
"""
Step 2: Folder Consolidation Script (After Cleanup)
===================================================
Run this AFTER running 1_cleanup_empty_folders.py

This merges all contents from your source folders into one Master folder.
- Duplicate folder names get renamed (_2, _3, etc.)
- Duplicate files are compared by content
- Identical files are skipped (saves space)
- Different files are renamed (_2, _3, etc.)
"""

import os
import sys
import shutil
import hashlib
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

# Log file location
LOG_FILE = None  # If None, will be: MASTER_FOLDER/consolidation_log.txt


class FolderConsolidator:
    def __init__(self, master_folder, log_file=None):
        self.master_folder = Path(master_folder)
        self.master_folder.mkdir(parents=True, exist_ok=True)

        if log_file is None:
            log_file = self.master_folder / "consolidation_log.txt"

        self.log_file = Path(log_file)
        self.stats = {
            'folders_copied': 0,
            'folders_renamed': 0,
            'files_copied': 0,
            'files_renamed': 0,
            'files_skipped': 0,
            'errors': 0
        }

    def log(self, message, print_also=True):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(log_message + "\n")
        if print_also:
            print(log_message)

    def get_file_hash(self, file_path):
        try:
            hash_obj = hashlib.md5()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except:
            return None

    def find_available_name(self, target_path, is_folder=False):
        if not target_path.exists():
            return target_path

        path_obj = Path(target_path)
        stem = path_obj.stem
        suffix = path_obj.suffix if not is_folder else ""
        parent = path_obj.parent

        counter = 2
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def are_files_identical(self, file1, file2):
        hash1 = self.get_file_hash(file1)
        hash2 = self.get_file_hash(file2)
        return (hash1 and hash2 and hash1 == hash2)

    def copy_file(self, source_file, dest_file):
        dest_file = Path(dest_file)
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if not dest_file.exists():
                shutil.copy2(source_file, dest_file)
                self.stats['files_copied'] += 1
                return True
            else:
                if self.are_files_identical(source_file, dest_file):
                    self.log(f"SKIP (identical): {source_file.name}", False)
                    self.stats['files_skipped'] += 1
                    return True
                else:
                    new_dest = self.find_available_name(dest_file, is_folder=False)
                    shutil.copy2(source_file, new_dest)
                    self.log(f"RENAME FILE: {dest_file.name} -> {new_dest.name}", False)
                    self.stats['files_renamed'] += 1
                    return True
        except Exception as e:
            self.log(f"ERROR copying file {source_file}: {e}", True)
            self.stats['errors'] += 1
            return False

    def copy_folder_tree(self, source_folder, dest_parent):
        source_folder = Path(source_folder)
        dest_folder = dest_parent / source_folder.name

        if dest_folder.exists():
            new_dest_folder = self.find_available_name(dest_folder, is_folder=True)
            self.log(f"CONFLICT: Folder '{dest_folder.name}' exists -> '{new_dest_folder.name}'", True)
            dest_folder = new_dest_folder
            self.stats['folders_renamed'] += 1

        dest_folder.mkdir(parents=True, exist_ok=True)
        self.stats['folders_copied'] += 1

        try:
            for item in source_folder.iterdir():
                if item.is_file():
                    self.copy_file(item, dest_folder / item.name)
                elif item.is_dir():
                    self.copy_folder_tree(item, dest_folder)

        except Exception as e:
            self.log(f"ERROR copying folder {source_folder}: {e}", True)
            self.stats['errors'] += 1

    def consolidate(self, source_folders):
        self.log("=" * 60, True)
        self.log("CONSOLIDATION STARTED", True)
        self.log("=" * 60, True)

        for i, source in enumerate(source_folders, 1):
            source_path = Path(source)
            self.log(f"\n[{i}/{len(source_folders)}] Processing: {source_path}", True)

            if not source_path.exists():
                self.log(f"ERROR: Source not found: {source_path}", True)
                continue

            try:
                # Iterate through contents of source folder
                for item in source_path.iterdir():
                    if item.is_file():
                        self.log(f"Processing file: {item.name}", False)
                        self.copy_file(item, self.master_folder / item.name)

                    elif item.is_dir():
                        self.log(f"Processing folder: {item.name}", False)
                        self.copy_folder_tree(item, self.master_folder)

            except Exception as e:
                self.log(f"ERROR processing {source}: {e}", True)

        self.log("\n" + "=" * 60, True)
        self.log("CONSOLIDATION COMPLETE", True)
        self.print_statistics()

    def print_statistics(self):
        self.log("\nSTATISTICS:", True)
        self.log(f"  Folders Copied:   {self.stats['folders_copied']}", True)
        self.log(f"  Folders Renamed:  {self.stats['folders_renamed']}", True)
        self.log(f"  Files Copied:     {self.stats['files_copied']}", True)
        self.log(f"  Files Renamed:    {self.stats['files_renamed']}", True)
        self.log(f"  Files Skipped:    {self.stats['files_skipped']}", True)
        self.log(f"  Errors:           {self.stats['errors']}", True)
        self.log(f"\nLog: {self.log_file}", True)

def main():
    print("\n" + "=" * 60)
    print("FOLDER CONSOLIDATION - STEP 2")
    print("=" * 60)

    if not MASTER_FOLDER or not SOURCE_FOLDERS:
        print("ERROR: Please configure MASTER_FOLDER and SOURCE_FOLDERS!")
        return

    print(f"\nDestination: {MASTER_FOLDER}")
    print(f"Sources: {len(SOURCE_FOLDERS)} folder(s)")

    confirm = input("\nProceed with consolidation? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    consolidator = FolderConsolidator(MASTER_FOLDER, LOG_FILE)
    consolidator.consolidate(SOURCE_FOLDERS)
    print("\n✅ Done!")

if __name__ == "__main__":
    main()