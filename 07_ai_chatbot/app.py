import argparse
from pathlib import Path
from chatbot import ChatSession


def run_cli_demo() -> None:
    bot = ChatSession()
    prompts = [
        "Hi! My name is Ardhy and I am building 7 Python mini projects today.",
        "What is my name and what am I building?",
    ]
    print("[07 AI Chatbot] Starting multi-turn conversation with memory...")
    for p in prompts:
        print(f"  User: {p}")
        reply = bot.send_message(p)
        print(f"  AI:   {reply}")

    history_file = Path(__file__).parent / "chat_history.json"
    bot.save_history(history_file)
    print(f"  Saved conversation history ({len(bot.history)} turns) to {history_file}")


def run_streamlit_ui() -> None:
    import streamlit as st

    st.set_page_config(page_title="07 - AI Chatbot", page_icon="🤖", layout="centered")
    st.title("🤖 Project 07: AI Chatbot with Memory")
    st.caption("Python + Anthropic SDK (Claude) + Streamlit + python-dotenv")

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = ChatSession()

    session: ChatSession = st.session_state.chat_session

    with st.sidebar:
        st.subheader("Chat Controls")
        st.write(f"Messages in memory: **{len(session.history)}**")
        if st.button("Clear Conversation"):
            session.clear()
            st.rerun()

    for msg in session.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask anything...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            reply = session.send_message(user_input)
            st.markdown(reply)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 07: AI Chatbot")
    parser.add_argument("--cli", action="store_true", help="Run multi-turn CLI demo")
    args, _ = parser.parse_known_args()
    if args.cli:
        run_cli_demo()
    else:
        run_streamlit_ui()
