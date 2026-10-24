import json
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(Path(__file__).parent / ".env")

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
DEFAULT_SYSTEM_PROMPT = (
    "You are a concise, helpful Python mentor assistant. "
    "You remember previous turns in the conversation and give practical code examples."
)


class ChatSession:
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT, model: str = DEFAULT_MODEL) -> None:
        self.system_prompt = system_prompt
        self.model = model
        self.history: List[Dict[str, str]] = []

    def send_message(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

        if api_key and api_key != "your_anthropic_api_key_here":
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.history,
            )
            reply = response.content[0].text
        else:
            reply = self._local_smart_reply(user_message)

        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _local_smart_reply(self, user_message: str) -> str:
        user_turns = [m["content"] for m in self.history if m["role"] == "user"]
        lower_msg = user_message.lower()
        if "remember" in lower_msg or "my name" in lower_msg or "what did i" in lower_msg:
            prev = user_turns[:-1]
            if prev:
                return (
                    f"[Claude Memory Mode] I remember our {len(prev)} earlier message(s)! "
                    f"You previously said: \"{prev[0]}\"."
                )
        return (
            f"[Claude SDK Ready | Turn #{len(user_turns)}] Received: \"{user_message}\". "
            f"(Set ANTHROPIC_API_KEY in .env for live Claude API calls; conversation history has {len(self.history)} messages.)"
        )

    def clear(self) -> None:
        self.history.clear()

    def save_history(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
