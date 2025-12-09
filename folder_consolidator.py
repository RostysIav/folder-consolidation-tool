#!/usr/bin/env python3
"""
Folder Consolidation & Deduplication Script
=============================================
This script consolidates files and folders from multiple source locations
into a single master directory, with intelligent duplicate handling.

Features:
- Copies folder structure recursively
- Renames duplicate folders with _2, _3, etc.
- Handles duplicate files (skip, rename, or compare)
- Creates detailed log file
- Progress reporting
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import hashlib


class FolderConsolidator:
    """Main class for folder consolidation and deduplication"""

    def __init__(self, master_folder, log_file=None):
        """
        Initialize the consolidator

        Args:
            master_folder (str): Destination folder where everything will be consolidated
            log_file (str): Path to log file (default: master_folder/consolidation_log.txt)
        """
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
        """Write to log file and optionally print to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")

        if print_also:
            print(log_message)

    def get_file_hash(self, file_path, chunk_size=8192):
        """Calculate MD5 hash of a file"""
        try:
            hash_obj = hashlib.md5()
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.log(f"ERROR: Could not hash file {file_path}: {e}", True)
            return None

    def find_available_name(self, target_path, is_folder=False):
        """Find an available name by adding _2, _3, etc. to avoid conflicts"""
        if not target_path.exists():
            return target_path

        path_obj = Path(target_path)
        stem = path_obj.stem if is_folder else path_obj.stem
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
        """Check if two files are identical using MD5 hash"""
        try:
            hash1 = self.get_file_hash(file1)
            hash2 = self.get_file_hash(file2)

            if hash1 and hash2:
                return hash1 == hash2
            return False
        except Exception as e:
            self.log(f"ERROR: Could not compare files {file1} and {file2}: {e}", False)
            return False

    def copy_file(self, source_file, dest_file):
        """
        Copy a file with duplicate handling

        Strategy:
        1. If destination doesn't exist: copy normally
        2. If exists and identical: skip
        3. If exists and different: rename source with _2, _3, etc.
        """
        source_file = Path(source_file)
        dest_file = Path(dest_file)

        # Ensure destination parent exists
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if not dest_file.exists():
                # File doesn't exist, just copy it
                shutil.copy2(source_file, dest_file)
                self.stats['files_copied'] += 1
                return True
            else:
                # File exists, check if identical
                if self.are_files_identical(source_file, dest_file):
                    self.log(f"SKIP (identical): {dest_file}", False)
                    self.stats['files_skipped'] += 1
                    return True
                else:
                    # Files are different, rename the new one
                    new_dest = self.find_available_name(dest_file, is_folder=False)
                    shutil.copy2(source_file, new_dest)
                    self.log(f"RENAME: {dest_file.name} → {new_dest.name}", False)
                    self.stats['files_renamed'] += 1
                    return True

        except Exception as e:
            self.log(f"ERROR copying {source_file}: {e}", True)
            self.stats['errors'] += 1
            return False

    def copy_folder_tree(self, source_folder, dest_parent=None):
        """
        Recursively copy folder tree to destination

        Args:
            source_folder (str): Source folder path
            dest_parent (str): Parent destination folder (default: master_folder)
        """
        source_folder = Path(source_folder)

        if dest_parent is None:
            dest_parent = self.master_folder
        else:
            dest_parent = Path(dest_parent)

        if not source_folder.exists():
            self.log(f"ERROR: Source folder does not exist: {source_folder}", True)
            self.stats['errors'] += 1
            return False

        # Create folder name in destination
        dest_folder = dest_parent / source_folder.name

        # Handle duplicate folder names
        if dest_folder.exists():
            self.log(f"RENAME FOLDER: Destination folder exists: {dest_folder.name}", True)
            dest_folder = self.find_available_name(dest_folder, is_folder=True)
            self.log(f"             Using new name: {dest_folder.name}", True)
            self.stats['folders_renamed'] += 1

        # Create the folder
        dest_folder.mkdir(parents=True, exist_ok=True)
        self.stats['folders_copied'] += 1
        self.log(f"FOLDER: {dest_folder}", False)

        # Copy all files and subdirectories
        try:
            for item in source_folder.iterdir():
                if item.is_file():
                    dest_file = dest_folder / item.name
                    self.copy_file(item, dest_file)

                elif item.is_dir():
                    # Recursively copy subdirectory
                    self.copy_folder_tree(item, dest_folder)

        except PermissionError:
            self.log(f"ERROR: Permission denied accessing {source_folder}", True)
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self.log(f"ERROR processing {source_folder}: {e}", True)
            self.stats['errors'] += 1
            return False

        return True

    def consolidate(self, source_folders):
        """
        Main consolidation method

        Args:
            source_folders (list): List of source folder paths to consolidate
        """
        self.log("=" * 60, True)
        self.log("FOLDER CONSOLIDATION STARTED", True)
        self.log("=" * 60, True)
        self.log(f"Master Folder: {self.master_folder}", True)
        self.log(f"Sources: {len(source_folders)} folder(s)", True)
        self.log("=" * 60, True)

        for i, source in enumerate(source_folders, 1):
            self.log(f"\n[{i}/{len(source_folders)}] Processing: {source}", True)
            self.copy_folder_tree(source)

        self.log("\n" + "=" * 60, True)
        self.log("CONSOLIDATION COMPLETE", True)
        self.log("=" * 60, True)
        self.print_statistics()

    def print_statistics(self):
        """Print consolidation statistics"""
        self.log("\nSTATISTICS:", True)
        self.log(f"  Folders Copied:   {self.stats['folders_copied']}", True)
        self.log(f"  Folders Renamed:  {self.stats['folders_renamed']}", True)
        self.log(f"  Files Copied:     {self.stats['files_copied']}", True)
        self.log(f"  Files Renamed:    {self.stats['files_renamed']}", True)
        self.log(f"  Files Skipped:    {self.stats['files_skipped']}", True)
        self.log(f"  Errors:           {self.stats['errors']}", True)
        self.log("\nLog saved to: " + str(self.log_file), True)


def main():
    """Main entry point - configure and run consolidation"""

    print("\n" + "=" * 60)
    print("FOLDER CONSOLIDATION TOOL")
    print("=" * 60)

    # Get master folder from user
    master_folder = input("\nEnter destination folder path for consolidated files: ").strip()

    if not master_folder:
        print("ERROR: Destination folder required!")
        return

    # Initialize consolidator
    consolidator = FolderConsolidator(master_folder)

    # Get source folders
    print("\nEnter source folders (one per line, empty line to finish):")
    source_folders = []

    while True:
        source = input("Source folder: ").strip()
        if not source:
            break
        if os.path.exists(source):
            source_folders.append(source)
            print(f"  ✓ Added: {source}")
        else:
            print(f"  ✗ Folder not found: {source}")

    if not source_folders:
        print("ERROR: No valid source folders provided!")
        return

    # Confirm before starting
    print(f"\n{'=' * 60}")
    print(f"Master Folder: {master_folder}")
    print(f"Source Folders: {len(source_folders)}")
    for i, folder in enumerate(source_folders, 1):
        print(f"  {i}. {folder}")
    print(f"{'=' * 60}")

    confirm = input("\nProceed with consolidation? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("Cancelled.")
        return

    # Run consolidation
    consolidator.consolidate(source_folders)

    print("\nDone! Check the log file for details.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
