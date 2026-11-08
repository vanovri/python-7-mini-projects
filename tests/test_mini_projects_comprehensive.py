"""Comprehensive isolated unit & integration tests across all 7 Python Mini Projects.

Uses temporary directories/SQLite databases (`tmp_path`) and `monkeypatch` mocks for external
HTTP/LLM/clipboard interfaces so tests execute deterministically with zero production pollution.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import matplotlib.pyplot as plt
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
for subdir in [
    "01_expense_tracker",
    "02_password_generator",
    "03_quiz_app",
    "04_weather_app",
    "05_file_organizer",
    "06_web_scraper",
    "07_ai_chatbot",
]:
    p = str(ROOT / subdir)
    if p not in sys.path:
        sys.path.insert(0, p)

import db as expense_db
import generator as pwd_gen
import quiz_engine
import weather_service
import organizer
import scraper
import chatbot


def _load_module_by_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 01. Expense Tracker (SQLite CRUD, Constraints, Aggregations, Charts)
# ---------------------------------------------------------------------------
class TestProject01ExpenseTracker:
    def test_crud_constraints_monthly_filters_and_budget_statuses(self, tmp_path: Path):
        db_file = tmp_path / "isolated_expenses.db"
        expense_db.init_db(db_file)

        # Negative amount or negative budget violates SQLite CHECK constraint
        with pytest.raises(sqlite3.IntegrityError):
            expense_db.add_expense("2026-10-01", "Food & Dining", -5.0, "Invalid", db_path=db_file)
        with pytest.raises(sqlite3.IntegrityError):
            expense_db.set_budget("Food & Dining", -100.0, db_path=db_file)

        id1 = expense_db.add_expense("2026-09-15", "Transportation", 40.0, "Bus", db_path=db_file)
        id2 = expense_db.add_expense("2026-10-02", "Food & Dining", 160.0, "Groceries", db_path=db_file)
        id3 = expense_db.add_expense("2026-10-05", "Shopping", 50.0, "Shirt", db_path=db_file)
        id4 = expense_db.add_expense("2026-10-09", "Entertainment", 120.0, "Concert", db_path=db_file)
        assert len({id1, id2, id3, id4}) == 4

        # Delete existing vs non-existent ID
        assert expense_db.delete_expense(id1, db_path=db_file) is True
        assert expense_db.delete_expense(99999, db_path=db_file) is False

        # Upsert budget via ON CONFLICT DO UPDATE
        expense_db.set_budget("Food & Dining", 250.0, db_path=db_file)
        expense_db.set_budget("Food & Dining", 200.0, db_path=db_file)  # 160 / 200 = 80% -> WARNING
        expense_db.set_budget("Shopping", 200.0, db_path=db_file)       # 50 / 200 = 25% -> OK
        expense_db.set_budget("Entertainment", 100.0, db_path=db_file)  # 120 / 100 = 120% -> EXCEEDED
        expense_db.set_budget("Health", 0.0, db_path=db_file)           # 0 / 0 -> 0% OK

        oct_df = expense_db.get_expenses_df("2026-10", db_path=db_file)
        assert len(oct_df) == 3

        all_cat = expense_db.get_category_summary(db_path=db_file)
        assert set(all_cat["category"]) == {"Food & Dining", "Shopping", "Entertainment"}

        mon_df = expense_db.get_monthly_totals(db_path=db_file)
        assert list(mon_df["month"]) == ["2026-10"]
        assert float(mon_df.iloc[0]["total"]) == 330.0

        alerts = {a["category"]: a for a in expense_db.check_budget_alerts("2026-10", db_path=db_file)}
        assert alerts["Food & Dining"]["status"] == "WARNING"
        assert alerts["Food & Dining"]["percent"] == 80.0
        assert alerts["Shopping"]["status"] == "OK"
        assert alerts["Entertainment"]["status"] == "EXCEEDED"
        assert alerts["Health"]["status"] == "OK"

    def test_seed_idempotency_and_chart_png_generation(self, tmp_path: Path):
        db_file = tmp_path / "seeded.db"
        first_count = expense_db.seed_sample_data(db_path=db_file)
        second_count = expense_db.seed_sample_data(db_path=db_file)
        assert first_count == 9
        assert second_count == 9  # Must not duplicate rows when called repeatedly

        exp_app = _load_module_by_path("exp_app_isolated", ROOT / "01_expense_tracker" / "app.py")
        chart_png = tmp_path / "chart.png"
        fig = exp_app.generate_charts(db_path=db_file, output_path=chart_png)
        plt.close(fig)
        assert chart_png.is_file() and chart_png.stat().st_size > 2000

        # Empty DB chart branch ("No category data" / "No monthly data")
        empty_db = tmp_path / "empty.db"
        expense_db.init_db(empty_db)
        fig_empty = exp_app.generate_charts(db_path=empty_db)
        plt.close(fig_empty)


# ---------------------------------------------------------------------------
# 02. Password Generator (Pools, Validation, Strength Tiers, Clipboard)
# ---------------------------------------------------------------------------
class TestProject02PasswordGenerator:
    def test_validation_character_pool_guarantees_and_strength_tiers(self, monkeypatch):
        with pytest.raises(ValueError, match="at least 4"):
            pwd_gen.generate_password(length=3)
        with pytest.raises(ValueError, match="At least one character set"):
            pwd_gen.generate_password(
                length=8,
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_symbols=False,
            )

        # Length 4 with all 4 pools enabled must include exactly 1 char from each pool
        p4 = pwd_gen.generate_password(length=4)
        s4 = pwd_gen.check_strength(p4)
        assert s4["length"] == 4
        assert s4["has_upper"] and s4["has_lower"] and s4["has_digit"] and s4["has_symbol"]
        assert s4["rating"] == "Medium"  # variety=4, length<8 -> score=4

        # Digits-only short password -> Weak
        digits_only = pwd_gen.generate_password(
            length=6, use_uppercase=False, use_lowercase=False, use_digits=True, use_symbols=False
        )
        assert digits_only.isdigit()
        assert pwd_gen.check_strength(digits_only)["rating"] == "Weak"

        # Clipboard helper handles missing or failing pyperclip gracefully
        monkeypatch.setattr(pwd_gen, "pyperclip", None)
        assert pwd_gen.copy_to_clipboard("secret") is False

        clipboard_box = {}
        fake_clip = SimpleNamespace(copy=lambda txt: clipboard_box.setdefault("val", txt))
        monkeypatch.setattr(pwd_gen, "pyperclip", fake_clip)
        assert pwd_gen.copy_to_clipboard("abc123") is True
        assert clipboard_box["val"] == "abc123"


# ---------------------------------------------------------------------------
# 03. Quiz App (JSON Loading, Seeded Shuffle, Pass/Fail & Finished Guard)
# ---------------------------------------------------------------------------
class TestProject03QuizApp:
    def test_load_questions_validation_and_full_quiz_lifecycle(self, tmp_path: Path):
        bad_json = tmp_path / "empty.json"
        bad_json.write_text("[]", encoding="utf-8")
        with pytest.raises(ValueError, match="non-empty JSON list"):
            quiz_engine.load_questions(bad_json)

        custom_bank = [
            {"id": 1, "question": "2+2?", "options": ["3", "4"], "answer": "4", "explanation": "Math"},
            {"id": 2, "question": "3+3?", "options": ["6", "7"], "answer": "6", "explanation": "Add"},
            {"id": 3, "question": "5+5?", "options": ["9", "10"], "answer": "10", "explanation": "Ten"},
        ]
        s1 = quiz_engine.QuizSession(questions=custom_bank, shuffle=True, seed=99)
        s2 = quiz_engine.QuizSession(questions=custom_bank, shuffle=True, seed=99)
        assert [q["id"] for q in s1.questions] == [q["id"] for q in s2.questions]

        # Answer 2/3 wrong -> 33.3% -> passed is False
        q0 = s1.current_question()
        assert q0 is not None
        s1.submit_answer(f"  {q0['answer']}  ")  # whitespace-tolerant match
        s1.submit_answer("wrong")
        s1.submit_answer("wrong")

        assert s1.is_finished is True
        assert s1.current_question() is None
        with pytest.raises(RuntimeError, match="already finished"):
            s1.submit_answer("4")

        summary = s1.summary()
        assert summary["score"] == 1
        assert summary["total"] == 3
        assert summary["percentage"] == 33.3
        assert summary["passed"] is False
        assert len(summary["history"]) == 3


# ---------------------------------------------------------------------------
# 04. Weather App (Mocked OpenWeather Primary, Fallback & City Not Found)
# ---------------------------------------------------------------------------
class TestProject04WeatherApp:
    def test_openweather_primary_and_automatic_open_meteo_fallback(self, monkeypatch):
        class FakeResp:
            def __init__(self, payload, ok=True, status_code=200):
                self._payload = payload
                self.ok = ok
                self.status_code = status_code

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"HTTP {self.status_code}")

            def json(self):
                return self._payload

        def fake_ow_get(url, params=None, timeout=10):
            if url.endswith("/weather"):
                return FakeResp(
                    {
                        "name": "Jakarta",
                        "sys": {"country": "ID"},
                        "main": {"temp": 30.44, "feels_like": 34.1, "humidity": 74},
                        "wind": {"speed": 5.0},  # 5 m/s -> 18.0 km/h
                        "weather": [{"description": "scattered clouds"}],
                    }
                )
            return FakeResp(
                {
                    "list": [
                        {"dt_txt": "2026-11-08 12:00:00", "main": {"temp": 31.2}, "weather": [{"description": "clear sky"}]}
                    ]
                }
            )

        monkeypatch.setenv("OPENWEATHER_API_KEY", "live_test_key_123")
        monkeypatch.setattr(weather_service.requests, "get", fake_ow_get)
        ow_res = weather_service.get_weather("Jakarta")
        assert ow_res["source"] == "OpenWeather API"
        assert ow_res["wind_kmh"] == 18.0
        assert len(ow_res["forecast"]) == 1

        # Simulate OpenWeather HTTP 401 failure -> automatically falls back to Open-Meteo
        def fake_fail_then_meteo(url, params=None, timeout=10):
            if "openweathermap.org" in url:
                return FakeResp({}, ok=False, status_code=401)
            if "geocoding-api.open-meteo.com" in url:
                return FakeResp(
                    {"results": [{"name": "Bandung", "country_code": "ID", "latitude": -6.9, "longitude": 107.6}]}
                )
            return FakeResp(
                {
                    "current": {
                        "temperature_2m": 23.6,
                        "apparent_temperature": 24.2,
                        "relative_humidity_2m": 82,
                        "weather_code": 61,
                        "wind_speed_10m": 9.4,
                    },
                    "daily": {
                        "time": ["2026-11-08", "2026-11-09"],
                        "temperature_2m_max": [26.0, 27.0],
                        "temperature_2m_min": [19.0, 20.0],
                        "weather_code": [61, 2],
                    },
                }
            )

        monkeypatch.setattr(weather_service.requests, "get", fake_fail_then_meteo)
        fb_res = weather_service.get_weather("Bandung")
        assert "Open-Meteo" in fb_res["source"]
        assert fb_res["sky"] == "slight rain"
        assert len(fb_res["forecast"]) == 2
        assert fb_res["forecast"][1]["sky"] == "partly cloudy"

        # Unknown city raises ValueError from fetch_open_meteo_live
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        monkeypatch.setattr(weather_service.requests, "get", lambda *a, **k: FakeResp({"results": []}))
        with pytest.raises(ValueError, match="not found"):
            weather_service.fetch_open_meteo_live("NowhereTownXYZ")


# ---------------------------------------------------------------------------
# 05. File Organizer (Extension Routing, Dry-Run, Collisions, Missing Folder)
# ---------------------------------------------------------------------------
class TestProject05FileOrganizer:
    def test_dry_run_collision_renaming_others_bucket_and_missing_dir(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            organizer.organize_folder(tmp_path / "does_not_exist")

        work = tmp_path / "downloads"
        work.mkdir()
        (work / "report.PDF").write_text("v1", encoding="utf-8")
        (work / "mystery.xyz").write_text("bin", encoding="utf-8")

        # Dry run must not create directories or move files
        preview = organizer.organize_folder(work, dry_run=True)
        assert len(preview) == 2
        assert (work / "report.PDF").exists()
        assert not (work / "Docs").exists()

        # Real run moves files into Docs and Others
        moved1 = organizer.organize_folder(work, dry_run=False)
        assert len(moved1) == 2
        assert (work / "Docs" / "report.PDF").read_text(encoding="utf-8") == "v1"
        assert (work / "Others" / "mystery.xyz").exists()

        # Drop another report.PDF with identical name -> collision safe rename report_1.PDF
        (work / "report.PDF").write_text("v2", encoding="utf-8")
        moved2 = organizer.organize_folder(work, dry_run=False)
        assert moved2[0]["destination"] == "Docs/report_1.PDF"
        assert (work / "Docs" / "report.PDF").read_text(encoding="utf-8") == "v1"
        assert (work / "Docs" / "report_1.PDF").read_text(encoding="utf-8") == "v2"


# ---------------------------------------------------------------------------
# 06. Web Scraper (Offline BS4 Parsers for Quotes, Books, HN & CSV Export)
# ---------------------------------------------------------------------------
class TestProject06WebScraper:
    def test_scrape_quotes_books_hackernews_and_csv_roundtrip(self, tmp_path: Path, monkeypatch):
        quotes_html = """
        <div class="quote">
          <span class="text">“Simplicity is prerequisite for reliability.”</span>
          <small class="author">Edsger W. Dijkstra</small>
          <div class="tags"><a class="tag">cs</a><a class="tag">engineering</a></div>
        </div>
        """
        books_html = """
        <article class="product_pod">
          <h3><a title="Designing Data-Intensive Applications">DDIA</a></h3>
          <p class="price_color">£42.50</p>
          <p class="instock availability">In stock</p>
        </article>
        """
        hn_html = """
        <tr class="athing">
          <td class="title"><span class="rank">1.</span></td>
          <td class="title"><span class="titleline"><a href="https://python.org">Python 3.14 Released</a></span></td>
        </tr>
        """

        monkeypatch.setattr(scraper, "fetch_html", lambda url, use_selenium=False: quotes_html)
        q_rows = scraper.scrape_quotes("http://local/quotes")
        assert q_rows == [
            {
                "quote": "Simplicity is prerequisite for reliability.",
                "author": "Edsger W. Dijkstra",
                "tags": "cs, engineering",
            }
        ]

        monkeypatch.setattr(scraper, "fetch_html", lambda url, use_selenium=False: books_html)
        b_rows = scraper.scrape_books("http://local/books")
        assert b_rows == [
            {
                "title": "Designing Data-Intensive Applications",
                "price": "£42.50",
                "availability": "In stock",
            }
        ]

        monkeypatch.setattr(scraper, "fetch_html", lambda url, use_selenium=False: hn_html)
        h_rows = scraper.scrape_hackernews("http://local/hn")
        assert h_rows == [{"rank": "1", "headline": "Python 3.14 Released", "link": "https://python.org"}]

        out_csv = tmp_path / "nested" / "books.csv"
        df = scraper.save_to_csv(b_rows, out_csv)
        assert out_csv.is_file()
        reloaded = pd.read_csv(out_csv)
        assert len(df) == len(reloaded) == 1
        assert reloaded.iloc[0]["title"] == "Designing Data-Intensive Applications"


# ---------------------------------------------------------------------------
# 07. AI Chatbot (Offline Memory, Mocked Anthropic API, Clear & Persistence)
# ---------------------------------------------------------------------------
class TestProject07AIChatbot:
    def test_offline_fallback_live_anthropic_client_branch_and_clear(self, tmp_path: Path, monkeypatch):
        # 1. Offline fallback mode (no valid API key)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
        session = chatbot.ChatSession(system_prompt="Test mentor", model="claude-test")
        r1 = session.send_message("I am learning pytest fixtures.")
        assert "[Claude SDK Ready | Turn #1]" in r1
        r2 = session.send_message("What did I say earlier?")
        assert "[Claude Memory Mode]" in r2
        assert "pytest fixtures" in r2

        # 2. Live Anthropic client branch via monkeypatched Anthropic class
        captured_calls = []

        class FakeAnthropic:
            def __init__(self, api_key: str):
                self.api_key = api_key
                self.messages = SimpleNamespace(create=self._create)

            def _create(self, **kwargs):
                captured_calls.append((self.api_key, kwargs))
                return SimpleNamespace(content=[SimpleNamespace(text="Mocked Claude response!")])

        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-mock-key")
        monkeypatch.setattr(chatbot, "Anthropic", FakeAnthropic)

        session.clear()
        assert session.history == []
        live_reply = session.send_message("Explain generators in 1 line.")
        assert live_reply == "Mocked Claude response!"
        assert len(captured_calls) == 1
        api_key_used, req_kwargs = captured_calls[0]
        assert api_key_used == "sk-ant-mock-key"
        assert req_kwargs["model"] == "claude-test"
        assert req_kwargs["system"] == "Test mentor"

        out_json = tmp_path / "chat.json"
        session.save_history(out_json)
        saved = json.loads(out_json.read_text(encoding="utf-8"))
        assert len(saved) == 2
        assert saved[1]["content"] == "Mocked Claude response!"
