import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from generator import generate_password, check_strength, copy_to_clipboard


def run_cli_demo(length: int = 16) -> None:
    pwd = generate_password(length=length)
    strength = check_strength(pwd)
    copied = copy_to_clipboard(pwd)
    print(f"[02 Password Generator] secrets.choice(chars) * {length} -> {pwd}")
    print(
        f"  Strength: {strength['rating']} ({strength['score']}/{strength['max_score']}) | Copied to clipboard: {copied}"
    )


def run_tkinter_gui() -> None:
    root = tk.Tk()
    root.title("Project 02: Password Generator")
    root.geometry("460x380")
    root.configure(padx=20, pady=20)

    length_var = tk.IntVar(value=16)
    upper_var = tk.BooleanVar(value=True)
    lower_var = tk.BooleanVar(value=True)
    digit_var = tk.BooleanVar(value=True)
    symbol_var = tk.BooleanVar(value=True)
    result_var = tk.StringVar(value="")
    strength_var = tk.StringVar(value="Click Generate to create a password")

    ttk.Label(root, text="🔐 Password Generator", font=("Segoe UI", 16, "bold")).pack(
        anchor="w", pady=(0, 10)
    )

    len_frame = ttk.Frame(root)
    len_frame.pack(fill="x", pady=5)
    ttk.Label(len_frame, text="Password Length:").pack(side="left")
    ttk.Spinbox(len_frame, from_=4, to=64, textvariable=length_var, width=8).pack(
        side="right"
    )

    ttk.Checkbutton(root, text="Uppercase (A-Z)", variable=upper_var).pack(anchor="w")
    ttk.Checkbutton(root, text="Lowercase (a-z)", variable=lower_var).pack(anchor="w")
    ttk.Checkbutton(root, text="Digits (0-9)", variable=digit_var).pack(anchor="w")
    ttk.Checkbutton(root, text="Symbols (!@#$...)", variable=symbol_var).pack(anchor="w")

    entry = ttk.Entry(root, textvariable=result_var, font=("Consolas", 13), justify="center")
    entry.pack(fill="x", pady=12)

    ttk.Label(root, textvariable=strength_var, font=("Segoe UI", 10, "italic")).pack(
        anchor="w", pady=(0, 10)
    )

    def on_generate():
        try:
            pwd = generate_password(
                length=length_var.get(),
                use_uppercase=upper_var.get(),
                use_lowercase=lower_var.get(),
                use_digits=digit_var.get(),
                use_symbols=symbol_var.get(),
            )
            result_var.set(pwd)
            info = check_strength(pwd)
            strength_var.set(
                f"Strength: {info['rating']} (Score {info['score']}/{info['max_score']})"
            )
        except ValueError as err:
            messagebox.showerror("Invalid Settings", str(err))

    def on_copy():
        pwd = result_var.get()
        if not pwd:
            return
        if copy_to_clipboard(pwd):
            strength_var.set("Copied to clipboard via pyperclip!")
        else:
            root.clipboard_clear()
            root.clipboard_append(pwd)
            strength_var.set("Copied to clipboard via Tkinter!")

    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="x", pady=8)
    ttk.Button(btn_frame, text="Generate Password", command=on_generate).pack(
        side="left", expand=True, fill="x", padx=(0, 5)
    )
    ttk.Button(btn_frame, text="Copy to Clipboard", command=on_copy).pack(
        side="right", expand=True, fill="x", padx=(5, 0)
    )

    on_generate()
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 02: Password Generator")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--length", type=int, default=16, help="Password length")
    args = parser.parse_args()
    if args.cli:
        run_cli_demo(length=args.length)
    else:
        run_tkinter_gui()
