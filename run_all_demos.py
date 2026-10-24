import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

COMMANDS = [
    ("01 Expense Tracker", [sys.executable, str(ROOT / "01_expense_tracker" / "app.py"), "--cli"]),
    ("02 Password Generator", [sys.executable, str(ROOT / "02_password_generator" / "app.py"), "--cli"]),
    ("03 Quiz App", [sys.executable, str(ROOT / "03_quiz_app" / "app.py"), "--cli"]),
    ("04 Weather App", [sys.executable, str(ROOT / "04_weather_app" / "app.py"), "--cli", "--city", "Delhi"]),
    ("05 File Organizer", [sys.executable, str(ROOT / "05_file_organizer" / "app.py")]),
    ("06 Web Scraper", [sys.executable, str(ROOT / "06_web_scraper" / "app.py"), "--target", "books"]),
    ("07 AI Chatbot", [sys.executable, str(ROOT / "07_ai_chatbot" / "app.py"), "--cli"]),
]


def main() -> None:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    print("=" * 72)
    print("EXECUTING ALL 7 PYTHON MINI PROJECTS (@the.natasha.ai)")
    print("=" * 72)
    for title, cmd in COMMANDS:
        print(f"\n>>> Running {title} ...")
        res = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if res.stdout:
            print(res.stdout.strip())
        if res.returncode != 0:
            print(f"[ERROR] {title} exited with code {res.returncode}")
            if res.stderr:
                print(res.stderr.strip())
            sys.exit(res.returncode)
    print("\n" + "=" * 72)
    print("ALL 7 PROJECTS EXECUTED SUCCESSFULLY!")
    print("=" * 72)


if __name__ == "__main__":
    main()
