# Folder Consolidation Tool

Python scripts to **clean up** and **consolidate scattered files/folders** into a single “master” directory, with **smart duplicate handling** (no overwrites).

## What this does

- **Copies** files/folders from many source locations into one destination folder.
- If a **folder name conflict** happens, it **renames** the incoming folder as `Name_2`, `Name_3`, etc.
- If a **file name conflict** happens:
  - If the files are **identical** (MD5 hash match) → **skip** the copy (saves space).
  - If the files are **different** → keep both by renaming the incoming one as `file_2.ext`, `file_3.ext`, etc.
- Creates detailed logs so you can audit what happened.

> ⚠️ Note: the cleanup step **deletes empty folders** in your source locations. Consolidation itself only copies.

---

## Repo contents

- `1_cleanup_empty_folders.py`  
  Step 1 — Deletes empty folders from your source folders (optional, but helps reduce noise).

- `consolidate_auto.py` ⭐ Recommended  
  Step 2 — Non-interactive path configuration (edit constants) + one-time consolidation into `MASTER_FOLDER`.

- `folder_consolidator.py`  
  Interactive version — prompts for destination + source folders and then runs consolidation.

- `consolidation_config.txt`  
  A helper template for listing your paths (not auto-loaded by the scripts unless you wire it in).

- `QUICK_START.txt`, `00_START_HERE.txt`, `BEFORE_AFTER_GUIDE.txt`  
  Guides + examples.

---

## Requirements

- Python **3.9+** recommended
- Works best on Windows, but should run on macOS/Linux too (paths will differ)

---

## Quick start (Windows)

### 1) (Optional) Clean empty folders first
1. Open `1_cleanup_empty_folders.py`
2. Edit:
   - `SOURCE_FOLDERS = [...]` (folders you want to scan/clean)
   - `LOG_FILE` (optional)
3. Run:
```bash
python 1_cleanup_empty_folders.py
```
It will ask for confirmation (`yes`) because it **deletes** empty folders.

### 2) Consolidate everything into one master folder
1. Open `consolidate_auto.py`
2. Edit:
   - `MASTER_FOLDER = r"C:\Path\To\Master"`
   - `SOURCE_FOLDERS = [r"...", r"..."]`
3. Run:
```bash
python consolidate_auto.py
```
It will ask for confirmation (`yes`) and then start copying + de-duplicating.

### Alternative: use the interactive script
If you don’t want to hardcode paths:
```bash
python folder_consolidator.py
```

---

## Path tips (Windows)

Use raw strings:
```py
MASTER_FOLDER = r"C:\Users\YourName\Archive_2024"
```

Or double backslashes:
```py
MASTER_FOLDER = "C:\\Users\\YourName\\Archive_2024"
```

Avoid setting your `MASTER_FOLDER` **inside** any of your `SOURCE_FOLDERS` (that can cause recursion / repeated copying).

---

## How duplicates are handled

### Duplicate folders
If the destination already has a folder with the same name, the incoming folder is renamed:
- `Documents` → `Documents_2` → `Documents_3` …

### Duplicate files
If a file name already exists at the destination:
- If content is **identical** → **skip** the incoming file.
- If content is **different** → keep both:
  - `report.pdf` and `report_2.pdf`

---

## Logging

- Cleanup step writes a log (default: `empty_folders_cleanup_log.txt`).
- Consolidation writes a log:
  - If `LOG_FILE = None`, it defaults to:  
    `MASTER_FOLDER/consolidation_log.txt`

Logs include:
- created/renamed folders
- copied/renamed/skipped files
- errors (permission, missing paths, etc.)
- summary statistics

---

## Safety notes (read before you run)

- Cleanup deletes **only empty folders**, but it still modifies your sources.
- Consolidation uses `shutil.copy2(...)` → originals remain intact.
- You should still:
  - spot-check the destination
  - read the log
  - only then decide whether to delete old scattered folders

---

## Troubleshooting

- **“Python not found”**  
  Install Python and ensure it’s added to PATH.

- **Permission errors**  
  Run terminal as Administrator (Windows) or check folder permissions.

- **It’s “slow”**  
  MD5 hashing is used to detect identical files. That costs time on large datasets.

- **Very long Windows paths**  
  Some systems hit path-length limits. If you see weird path errors, consider enabling long paths in Windows, or consolidate to a shorter destination path like `D:\Archive`.

---

## License

MIT — see `LICENSE`.

---

## Idea for improvement (if you want to PR yourself 😄)

- Load `consolidation_config.txt` automatically (so you edit paths in one place).
- Add an optional “dry run” mode.
- Add exclude rules (e.g., skip caches like Chrome/Temp).
