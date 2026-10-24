import sys
from pathlib import Path
from datetime import date
import streamlit as st

ROOT = Path(__file__).parent
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

from db import (
    CATEGORIES,
    init_db,
    seed_sample_data,
    add_expense,
    set_budget,
    get_expenses_df,
    check_budget_alerts,
)
from generator import generate_password, check_strength, copy_to_clipboard
from quiz_engine import QuizSession
from weather_service import get_weather
from organizer import create_demo_messy_folder, organize_folder
from scraper import scrape_books, scrape_quotes, scrape_hackernews, save_to_csv
from chatbot import ChatSession

st.set_page_config(page_title="7 Python Mini Projects Hub", page_icon="🐍", layout="wide")

st.sidebar.title("🐍 7 Python Mini Projects")
project_choice = st.sidebar.radio(
    "Select Project:",
    [
        "01. Expense Tracker",
        "02. Password Generator",
        "03. Quiz App",
        "04. Weather App",
        "05. File Organizer",
        "06. Web Scraper",
        "07. AI Chatbot",
    ],
)

if project_choice.startswith("01"):
    from app import generate_charts

    init_db()
    seed_sample_data()
    st.title("01. Expense Tracker")
    st.caption("Tech Stack: Python • SQLite • Pandas • Matplotlib • Streamlit")
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("hub_exp"):
            d = st.date_input("Date", value=date.today())
            cat = st.selectbox("Category", CATEGORIES)
            amt = st.number_input("Amount ($)", min_value=0.01, value=20.0)
            desc = st.text_input("Description", value="Coffee & snack")
            if st.form_submit_button("Add Expense"):
                add_expense(str(d), cat, amt, desc)
                st.rerun()
    with c2:
        for alert in check_budget_alerts("2026-10"):
            st.metric(
                f"{alert['category']} ({alert['status']})",
                f"${alert['spent']:.2f} / ${alert['limit']:.2f}",
                f"{alert['percent']}%",
            )
    st.pyplot(generate_charts())
    st.dataframe(get_expenses_df(), use_container_width=True)

elif project_choice.startswith("02"):
    st.title("02. Password Generator")
    st.caption("Tech Stack: Python • secrets • string • Tkinter • pyperclip")
    length = st.slider("Password Length", 4, 64, 16)
    c1, c2, c3, c4 = st.columns(4)
    u = c1.checkbox("Uppercase", True)
    l = c2.checkbox("Lowercase", True)
    d = c3.checkbox("Digits", True)
    s = c4.checkbox("Symbols", True)
    if st.button("Generate Strong Password", type="primary"):
        pwd = generate_password(length, u, l, d, s)
        info = check_strength(pwd)
        copy_to_clipboard(pwd)
        st.code(pwd, language="text")
        st.success(f"Strength: {info['rating']} ({info['score']}/{info['max_score']}) | Copied to clipboard!")

elif project_choice.startswith("03"):
    st.title("03. Quiz App")
    st.caption("Tech Stack: Python • JSON • random • Tkinter")
    if "quiz" not in st.session_state:
        st.session_state.quiz = QuizSession(shuffle=True)
    quiz: QuizSession = st.session_state.quiz
    if quiz.is_finished:
        res = quiz.summary()
        st.balloons()
        st.success(f"Final Score: {res['score']} / {res['total']} ({res['percentage']}%)")
        if st.button("Restart Quiz"):
            st.session_state.quiz = QuizSession(shuffle=True)
            st.rerun()
    else:
        q = quiz.current_question()
        st.subheader(f"Q{quiz.current_index + 1}/{quiz.total_questions}: {q['question']}")
        choice = st.radio("Choose an option:", q["options"], key=f"q_{quiz.current_index}")
        if st.button("Submit Answer", type="primary"):
            quiz.submit_answer(choice)
            st.rerun()

elif project_choice.startswith("04"):
    st.title("04. Weather App")
    st.caption("Tech Stack: Python • Requests • OpenWeather API / Open-Meteo • JSON • python-dotenv • Streamlit")
    city = st.text_input("Enter City", value="Delhi")
    if st.button("Fetch Live Weather", type="primary"):
        data = get_weather(city)
        c1, c2, c3 = st.columns(3)
        c1.metric("Temp", f"{data['temp']} °C")
        c2.metric("Humidity", f"{data['humidity']}%")
        c3.metric("Sky", data["sky"].title())
        st.table(data["forecast"])

elif project_choice.startswith("05"):
    st.title("05. File Organizer")
    st.caption("Tech Stack: Python • pathlib • shutil • watchdog")
    if st.button("Create & Auto-Sort Demo Downloads Folder", type="primary"):
        demo_dir = ROOT / "05_file_organizer" / "demo_downloads"
        create_demo_messy_folder(demo_dir)
        res = organize_folder(demo_dir)
        st.success(f"Sorted {len(res)} files in {demo_dir}")
        st.table(res)

elif project_choice.startswith("06"):
    st.title("06. Web Scraper")
    st.caption("Tech Stack: Python • Requests • BeautifulSoup • Pandas • Selenium")
    target = st.selectbox("Select Target Website", ["books", "quotes", "hn"])
    if st.button("Scrape & Save CSV", type="primary"):
        out_dir = ROOT / "06_web_scraper" / "output"
        if target == "books":
            rows = scrape_books()
        elif target == "quotes":
            rows = scrape_quotes()
        else:
            rows = scrape_hackernews()
        df = save_to_csv(rows, out_dir / f"{target}.csv")
        st.success(f"Scraped {len(df)} items and saved to {out_dir / f'{target}.csv'}")
        st.dataframe(df, use_container_width=True)

elif project_choice.startswith("07"):
    st.title("07. AI Chatbot")
    st.caption("Tech Stack: Python • Anthropic SDK • Claude • Streamlit • python-dotenv")
    if "hub_chat" not in st.session_state:
        st.session_state.hub_chat = ChatSession()
    chat: ChatSession = st.session_state.hub_chat
    for m in chat.history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    prompt = st.chat_input("Say something to the chatbot...")
    if prompt:
        chat.send_message(prompt)
        st.rerun()
