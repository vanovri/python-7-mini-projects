import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from quiz_engine import QuizSession


def run_cli_demo() -> None:
    session = QuizSession(shuffle=True, seed=42)
    print(f"[03 Quiz App] Loaded {session.total_questions} questions from JSON (shuffled).")
    while not session.is_finished:
        q = session.current_question()
        # Simulate picking the right answer for most questions to demonstrate checking
        chosen = q["answer"] if session.current_index % 4 != 3 else q["options"][0]
        res = session.submit_answer(chosen)
        status = "CORRECT" if res["is_correct"] else f"WRONG (Ans: {res['correct_answer']})"
        print(f"  Q{res['question_number']}: {q['question'][:55]}... -> {chosen} [{status}]")

    result = session.summary()
    print(
        f"  Final Score: {result['score']}/{result['total']} ({result['percentage']}%) | Passed: {result['passed']}"
    )


def run_tkinter_gui() -> None:
    session = QuizSession(shuffle=True)
    root = tk.Tk()
    root.title("Project 03: Quiz App")
    root.geometry("560x420")
    root.configure(padx=24, pady=24)

    header_var = tk.StringVar()
    question_var = tk.StringVar()
    choice_var = tk.StringVar()
    feedback_var = tk.StringVar()

    ttk.Label(root, textvariable=header_var, font=("Segoe UI", 11, "bold")).pack(
        anchor="w", pady=(0, 6)
    )
    ttk.Label(
        root, textvariable=question_var, font=("Segoe UI", 13), wraplength=500, justify="left"
    ).pack(anchor="w", pady=(0, 14))

    options_frame = ttk.Frame(root)
    options_frame.pack(fill="x", pady=6)
    radio_buttons = []
    for _ in range(4):
        rb = ttk.Radiobutton(options_frame, text="", variable=choice_var, value="")
        rb.pack(anchor="w", pady=4)
        radio_buttons.append(rb)

    ttk.Label(
        root, textvariable=feedback_var, font=("Segoe UI", 10, "italic"), wraplength=500
    ).pack(anchor="w", pady=10)

    def load_current_question():
        q = session.current_question()
        if q is None:
            res = session.summary()
            messagebox.showinfo(
                "Quiz Complete!",
                f"Final Score: {res['score']} / {res['total']} ({res['percentage']}%)",
            )
            root.destroy()
            return
        header_var.set(
            f"Question {session.current_index + 1} of {session.total_questions}  |  Score: {session.score}"
        )
        question_var.set(q["question"])
        choice_var.set("")
        for idx, opt in enumerate(q["options"]):
            radio_buttons[idx].config(text=opt, value=opt)

    def on_submit():
        selected = choice_var.get()
        if not selected:
            messagebox.showwarning("Select an Option", "Please choose an answer first.")
            return
        res = session.submit_answer(selected)
        if res["is_correct"]:
            feedback_var.set(f"✅ Correct! {res['explanation']}")
        else:
            feedback_var.set(
                f"❌ Wrong. Correct answer: {res['correct_answer']}. {res['explanation']}"
            )
        load_current_question()

    ttk.Button(root, text="Submit Answer", command=on_submit).pack(anchor="e", pady=12)
    load_current_question()
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 03: Quiz App")
    parser.add_argument("--cli", action="store_true", help="Run automated CLI quiz demo")
    args = parser.parse_args()
    if args.cli:
        run_cli_demo()
    else:
        run_tkinter_gui()
