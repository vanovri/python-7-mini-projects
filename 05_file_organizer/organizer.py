import shutil
import time
from pathlib import Path
from typing import Dict, List, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CATEGORY_EXTENSIONS: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
    "Docs": [".pdf", ".docx", ".doc", ".txt", ".md", ".xlsx", ".csv", ".pptx"],
    "Videos": [".mp4", ".mov", ".mkv", ".avi", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".sql"],
}


def get_category_for_extension(ext: str) -> str:
    ext_lower = ext.lower()
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if ext_lower in extensions:
            return category
    return "Others"


def organize_single_file(file_path: Path, base_folder: Path, dry_run: bool = False) -> Dict[str, Any] | None:
    if not file_path.is_file():
        return None
    category = get_category_for_extension(file_path.suffix)
    target_dir = base_folder / category
    target_path = target_dir / file_path.name

    # Handle filename collisions safely
    counter = 1
    while target_path.exists() and target_path.resolve() != file_path.resolve():
        target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(target_path))

    return {
        "file": file_path.name,
        "extension": file_path.suffix,
        "category": category,
        "destination": f"{category}/{target_path.name}",
    }


def organize_folder(folder_path: Path, dry_run: bool = False) -> List[Dict[str, Any]]:
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Directory not found: {folder}")

    moved_files: List[Dict[str, Any]] = []
    for item in sorted(folder.iterdir()):
        if item.is_file():
            res = organize_single_file(item, folder, dry_run=dry_run)
            if res:
                moved_files.append(res)
    return moved_files


def create_demo_messy_folder(demo_dir: Path) -> Path:
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    demo_dir.mkdir(parents=True, exist_ok=True)

    dummy_files = [
        "vacation_photo.jpg",
        "ui_mockup.png",
        "resume_2026.pdf",
        "project_notes.docx",
        "tutorial_clip.mp4",
        "screen_recording.mov",
        "backup_bundle.zip",
        "podcast_episode.mp3",
        "automation_script.py",
    ]
    for fname in dummy_files:
        (demo_dir / fname).write_text(f"# Dummy content for {fname}\n", encoding="utf-8")
    return demo_dir


class AutoOrganizeHandler(FileSystemEventHandler):
    def __init__(self, watch_dir: Path) -> None:
        super().__init__()
        self.watch_dir = Path(watch_dir)

    def on_created(self, event):
        if event.is_directory:
            return
        src_path = Path(event.src_path)
        if src_path.parent.resolve() == self.watch_dir.resolve():
            time.sleep(0.1)
            res = organize_single_file(src_path, self.watch_dir)
            if res:
                print(f"  [Watchdog] Auto-moved {res['file']} -> {res['destination']}")


def watch_folder(folder_path: Path, duration_seconds: float | None = None) -> None:
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    event_handler = AutoOrganizeHandler(folder)
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=False)
    observer.start()
    print(f"Watching folder for new files: {folder}")
    try:
        start = time.time()
        while True:
            time.sleep(0.25)
            if duration_seconds is not None and (time.time() - start) >= duration_seconds:
                break
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
