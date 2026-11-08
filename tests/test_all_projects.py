import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
for subdir in [
    "01_expense_tracker",
    "02_password_generator",
    "03_quiz_app",
    "04_weather_app",
    "05_file_organizer",
    "06_web_scraper",
    "07_ai_chatbot",
]:
    sys.path.insert(0, str(ROOT / subdir))

from db import init_db, add_expense, set_budget, get_category_summary, check_budget_alerts
from generator import generate_password, check_strength
from quiz_engine import QuizSession
from weather_service import get_weather
from organizer import create_demo_messy_folder, organize_folder
from scraper import scrape_quotes, save_to_csv
from chatbot import ChatSession
import weather_service
import scraper
from types import SimpleNamespace


def test_01_expense_tracker(tmp_path: Path):
    db_file = tmp_path / "test_expenses.db"
    init_db(db_file)
    add_expense("2026-10-10", "Food & Dining", 120.0, "Groceries", db_path=db_file)
    add_expense("2026-10-12", "Food & Dining", 90.0, "Dinner", db_path=db_file)
    set_budget("Food & Dining", 200.0, db_path=db_file)

    summary = get_category_summary("2026-10", db_path=db_file)
    assert not summary.empty
    assert float(summary.iloc[0]["total"]) == 210.0

    alerts = check_budget_alerts("2026-10", db_path=db_file)
    assert len(alerts) == 1
    assert alerts[0]["status"] == "EXCEEDED"


def test_02_password_generator():
    pwd = generate_password(length=20)
    assert len(pwd) == 20
    info = check_strength(pwd)
    assert info["rating"] == "Strong"
    assert info["has_upper"] and info["has_lower"] and info["has_digit"] and info["has_symbol"]


def test_03_quiz_app():
    quiz = QuizSession(shuffle=False)
    total = quiz.total_questions
    assert total >= 5
    first_q = quiz.current_question()
    res = quiz.submit_answer(first_q["answer"])
    assert res["is_correct"] is True
    assert quiz.score == 1


def test_04_weather_app(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params, timeout))
        if "geocoding-api" in url:
            assert params["name"] == "Delhi"
            payload = {"results": [{"name": "Delhi", "country_code": "IN", "latitude": 28.6, "longitude": 77.2}]}
        else:
            assert params["latitude"] == 28.6
            assert params["longitude"] == 77.2
            payload = {
                "current": {"temperature_2m": 31.5, "relative_humidity_2m": 52,
                            "apparent_temperature": 33.0, "weather_code": 2, "wind_speed_10m": 8.4},
                "daily": {"time": ["2026-11-08"], "temperature_2m_max": [34.0],
                          "temperature_2m_min": [24.0], "weather_code": [2]},
            }
        return SimpleNamespace(json=lambda: payload, raise_for_status=lambda: None)

    monkeypatch.setattr(weather_service.requests, "get", fake_get)
    data = get_weather("Delhi")
    assert "temp" in data
    assert "humidity" in data
    assert "sky" in data
    assert isinstance(data["forecast"], list) and len(data["forecast"]) > 0
    assert data["temp"] == 31.5 and data["humidity"] == 52
    assert data["forecast"][0]["temp"] == 29.0
    assert len(calls) == 2


def test_05_file_organizer(tmp_path: Path):
    demo_dir = tmp_path / "messy"
    create_demo_messy_folder(demo_dir)
    moved = organize_folder(demo_dir)
    assert len(moved) == 9
    assert (demo_dir / "Images" / "vacation_photo.jpg").exists()
    assert (demo_dir / "Docs" / "resume_2026.pdf").exists()
    assert (demo_dir / "Videos" / "tutorial_clip.mp4").exists()
    assert (demo_dir / "Archives" / "backup_bundle.zip").exists()


def test_06_web_scraper(tmp_path: Path, monkeypatch):
    html = '<div class="quote"><span class="text">A deterministic fixture.</span><small class="author">Test Author</small><div class="tags"><a class="tag">testing</a></div></div>'

    def fake_get(url, headers, timeout):
        assert url == "https://quotes.toscrape.com/" and timeout == 12
        assert "User-Agent" in headers
        return SimpleNamespace(text=html, encoding="utf-8", raise_for_status=lambda: None)

    monkeypatch.setattr(scraper.requests, "get", fake_get)
    rows = scrape_quotes()
    assert len(rows) > 0
    assert "quote" in rows[0] and "author" in rows[0]
    assert rows[0] == {"quote": "A deterministic fixture.", "author": "Test Author", "tags": "testing"}
    csv_file = tmp_path / "quotes.csv"
    df = save_to_csv(rows, csv_file)
    assert csv_file.exists()
    assert len(df) == len(rows)


def test_07_ai_chatbot(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    session = ChatSession()
    r1 = session.send_message("Hello, my name is Ardhy.")
    r2 = session.send_message("Do you remember my name?")
    assert len(session.history) == 4
    assert "Ardhy" in r2
    hist_path = tmp_path / "history.json"
    session.save_history(hist_path)
    assert hist_path.exists()
