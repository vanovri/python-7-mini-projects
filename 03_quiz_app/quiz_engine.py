import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_QUESTIONS_PATH = Path(__file__).parent / "questions.json"


def load_questions(json_path: Path = DEFAULT_QUESTIONS_PATH) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError("Questions file must contain a non-empty JSON list.")
    return data


class QuizSession:
    def __init__(
        self,
        questions: Optional[List[Dict[str, Any]]] = None,
        shuffle: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        raw = list(questions) if questions is not None else load_questions()
        self.questions: List[Dict[str, Any]] = [dict(q) for q in raw]
        self.rng = random.Random(seed)
        if shuffle:
            self.rng.shuffle(self.questions)
        self.current_index: int = 0
        self.score: int = 0
        self.history: List[Dict[str, Any]] = []

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)

    def current_question(self) -> Optional[Dict[str, Any]]:
        if self.is_finished:
            return None
        return self.questions[self.current_index]

    def submit_answer(self, selected_option: str) -> Dict[str, Any]:
        if self.is_finished:
            raise RuntimeError("Quiz is already finished.")
        q = self.questions[self.current_index]
        correct_answer = q["answer"]
        is_correct = selected_option.strip() == correct_answer.strip()
        if is_correct:
            self.score += 1

        record = {
            "question_number": self.current_index + 1,
            "question": q["question"],
            "selected": selected_option,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        }
        self.history.append(record)
        self.current_index += 1
        return record

    def summary(self) -> Dict[str, Any]:
        total = self.total_questions
        pct = round((self.score / total) * 100, 1) if total > 0 else 0.0
        return {
            "score": self.score,
            "total": total,
            "percentage": pct,
            "passed": pct >= 70.0,
            "history": self.history,
        }
