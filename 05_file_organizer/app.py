import argparse
from pathlib import Path
from organizer import create_demo_messy_folder, organize_folder, watch_folder


def run_cli_demo() -> None:
    demo_dir = Path(__file__).parent / "demo_downloads"
    create_demo_messy_folder(demo_dir)
    print(f"[05 File Organizer] Created messy folder at: {demo_dir}")
    results = organize_folder(demo_dir)
    for r in results:
        print(f"  {r['file']} ({r['extension']}) -> {r['destination']}")
    print(f"  Organized {len(results)} files into clean category folders!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 05: File Organizer")
    parser.add_argument("--folder", type=str, help="Target folder to organize")
    parser.add_argument("--watch", action="store_true", help="Watch folder in real time with watchdog")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()

    if args.folder:
        target = Path(args.folder)
        moved = organize_folder(target, dry_run=args.dry_run)
        for item in moved:
            print(f"{item['file']} -> {item['destination']}")
        if args.watch and not args.dry_run:
            watch_folder(target)
    else:
        run_cli_demo()
