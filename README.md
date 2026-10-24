# 7 Python Mini Projects (@the.natasha.ai)

Complete implementation of all 7 Python Mini Projects from [`@the.natasha.ai` Instagram carousel (`De10gSgE-LW`)](https://www.instagram.com/p/De10gSgE-LW/):

| # | Project | Core Workflow | Tech Stack | Entry Point |
|---|---------|---------------|------------|-------------|
| 01 | **Expense Tracker** | Add expense → Save to SQLite → Group by category → Monthly charts → Budget alerts | `Python`, `SQLite`, `Pandas`, `Matplotlib`, `Streamlit` | `01_expense_tracker/app.py` |
| 02 | **Password Generator** | Pick length → Char sets → Random pick (`secrets.choice`) → Strength check → Copy it | `Python`, `secrets`, `string`, `Tkinter`, `pyperclip` | `02_password_generator/app.py` |
| 03 | **Quiz App** | Load JSON → Shuffle → Ask question → Check answer → Final score | `Python`, `JSON`, `random`, `Tkinter` | `03_quiz_app/app.py` |
| 04 | **Weather App** | Enter city → API request → Weather API → Parse JSON → Show forecast | `Python`, `Requests`, `OpenWeather API` (+ Open-Meteo fallback), `JSON`, `python-dotenv`, `Streamlit` | `04_weather_app/app.py` |
| 05 | **File Organizer** | Scan folder → Read extension → Match category → Move file → Clean folder | `Python`, `pathlib`, `shutil`, `watchdog` | `05_file_organizer/app.py` |
| 06 | **Web Scraper** | Target URL → Fetch HTML → Parse tags → Extract data → Save CSV | `Python`, `Requests`, `BeautifulSoup`, `Pandas`, `Selenium` | `06_web_scraper/app.py` |
| 07 | **AI Chatbot** | Your message → Chat history → Claude API → AI reply → Chat UI | `Python`, `Anthropic SDK`, `Claude`, `Streamlit`, `python-dotenv` | `07_ai_chatbot/app.py` |

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run All 7 Projects End-to-End (CLI Demo)
```bash
python run_all_demos.py
```

### 3. Launch Unified Streamlit Hub (All 7 Projects in One UI)
```bash
streamlit run dashboard.py
```

### 4. Run Automated Tests
```bash
pytest -v
```
