# Graph Report - python-7-mini-projects  (2026-10-24)

## Corpus Check
- 21 files · ~7,294 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 106 nodes · 237 edges · 10 communities
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ee6ffea4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- init_db
- organizer.py
- QuizSession
- test_all_projects.py
- scraper.py
- ChatSession
- 02_password_generator/app.py
- Quick Start

## God Nodes (most connected - your core abstractions)
1. `init_db()` - 15 edges
2. `get_connection()` - 11 edges
3. `QuizSession` - 11 edges
4. `ChatSession` - 10 edges
5. `get_category_summary()` - 9 edges
6. `check_budget_alerts()` - 9 edges
7. `seed_sample_data()` - 9 edges
8. `run_cli_demo()` - 8 edges
9. `run_streamlit_ui()` - 8 edges
10. `add_expense()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_03_quiz_app()` --uses--> `QuizSession`  [INFERRED]
  tests/test_all_projects.py → 03_quiz_app/quiz_engine.py
- `test_04_weather_app()` --calls--> `get_weather()`  [INFERRED]
  tests/test_all_projects.py → 04_weather_app/weather_service.py
- `test_07_ai_chatbot()` --uses--> `ChatSession`  [INFERRED]
  tests/test_all_projects.py → 07_ai_chatbot/chatbot.py
- `test_01_expense_tracker()` --calls--> `init_db()`  [INFERRED]
  tests/test_all_projects.py → 01_expense_tracker/db.py
- `test_01_expense_tracker()` --calls--> `add_expense()`  [INFERRED]
  tests/test_all_projects.py → 01_expense_tracker/db.py

## Import Cycles
- None detected.

## Communities (10 total, 0 thin omitted)

### Community 0 - "init_db"
Cohesion: 0.38
Nodes (19): generate_charts(), Path, run_cli_demo(), run_streamlit_ui(), add_expense(), check_budget_alerts(), delete_expense(), get_category_summary() (+11 more)

### Community 1 - "organizer.py"
Cohesion: 0.29
Nodes (11): run_cli_demo(), AutoOrganizeHandler, create_demo_messy_folder(), get_category_for_extension(), organize_folder(), organize_single_file(), Any, Path (+3 more)

### Community 2 - "QuizSession"
Cohesion: 0.23
Nodes (6): run_cli_demo(), run_tkinter_gui(), load_questions(), Any, Path, QuizSession

### Community 3 - "test_all_projects.py"
Cohesion: 0.26
Nodes (10): run_cli_demo(), run_streamlit_ui(), fetch_open_meteo_live(), fetch_openweather(), get_weather(), Any, Path, test_03_quiz_app() (+2 more)

### Community 4 - "scraper.py"
Cohesion: 0.39
Nodes (10): run_cli_demo(), fetch_html(), Any, DataFrame, Path, save_to_csv(), scrape_books(), scrape_hackernews() (+2 more)

### Community 5 - "ChatSession"
Cohesion: 0.23
Nodes (4): run_cli_demo(), run_streamlit_ui(), ChatSession, Path

### Community 6 - "02_password_generator/app.py"
Cohesion: 0.50
Nodes (7): run_cli_demo(), run_tkinter_gui(), check_strength(), copy_to_clipboard(), generate_password(), Any, test_02_password_generator()

### Community 7 - "Quick Start"
Cohesion: 0.29
Nodes (6): 1. Install Dependencies, 2. Run All 7 Projects End-to-End (CLI Demo), 3. Launch Unified Streamlit Hub (All 7 Projects in One UI), 4. Run Automated Tests, 7 Python Mini Projects (@the.natasha.ai), Quick Start

## Knowledge Gaps
- **4 isolated node(s):** `1. Install Dependencies`, `2. Run All 7 Projects End-to-End (CLI Demo)`, `3. Launch Unified Streamlit Hub (All 7 Projects in One UI)`, `4. Run Automated Tests`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 20 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChatSession` connect `ChatSession` to `test_all_projects.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `QuizSession` connect `QuizSession` to `test_all_projects.py`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `test_01_expense_tracker()` connect `init_db` to `test_all_projects.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `1. Install Dependencies`, `2. Run All 7 Projects End-to-End (CLI Demo)`, `3. Launch Unified Streamlit Hub (All 7 Projects in One UI)` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._