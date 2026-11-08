# Python 7 mini projects technical debt

Reviewed 2026-11-08 against current source. Exact 1-based source locations appear below. All diffs are complete proposals, not applied edits. This documentation-only crosscheck does not assert GUI or live-provider execution.

## 1. Resolve the expense app explicitly and show the current budget month

Location: `dashboard.py:7-18,52-53,70` and `01_expense_tracker/app.py:117-119`. All seven subdirectories contain app.py. Prepending them reverses their search order, so a clean dashboard process resolves `from app import generate_charts` to the chatbot app, which lacks that function. Existing sys.modules state can change the collision result. Import the expense UI by its exact path. Current-day expense forms also conflict with a fixed October 2026 alert month. The CLI demonstration's October sample report is intentional and remains unchanged in the proposal.

```diff
diff --git a/dashboard.py b/dashboard.py
--- a/dashboard.py
+++ b/dashboard.py
@@ -1,3 +1,4 @@
+import importlib.util
 import sys
 from pathlib import Path
 from datetime import date
@@ -50,7 +51,12 @@
 )
 
 if project_choice.startswith("01"):
-    from app import generate_charts
+    spec = importlib.util.spec_from_file_location("expense_app", ROOT / "01_expense_tracker" / "app.py")
+    if spec is None or spec.loader is None:
+        raise ImportError("Could not load expense app")
+    expense_app = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(expense_app)
+    generate_charts = expense_app.generate_charts
 
     init_db()
     seed_sample_data()
@@ -67,7 +73,7 @@
                 add_expense(str(d), cat, amt, desc)
                 st.rerun()
     with c2:
-        for alert in check_budget_alerts("2026-10"):
+        for alert in check_budget_alerts(date.today().strftime("%Y-%m")):
             st.metric(
                 f"{alert['category']} ({alert['status']})",
                 f"${alert['spent']:.2f} / ${alert['limit']:.2f}",
diff --git a/01_expense_tracker/app.py b/01_expense_tracker/app.py
--- a/01_expense_tracker/app.py
+++ b/01_expense_tracker/app.py
@@ -114,9 +114,10 @@
                 st.rerun()
 
     st.divider()
-    alerts = check_budget_alerts("2026-10")
+    active_month = date.today().strftime("%Y-%m")
+    alerts = check_budget_alerts(active_month)
     if alerts:
-        st.subheader("🎯 Budget Alerts (2026-10)")
+        st.subheader(f"🎯 Budget Alerts ({active_month})")
         cols = st.columns(len(alerts))
         for idx, a in enumerate(alerts):
             delta_color = "inverse" if a["status"] == "EXCEEDED" else "normal"
```

Validation: Exercise the dashboard expense branch in a fresh process and after visiting other projects. Add a current-month expense and confirm both UIs query that month. A future packaging refactor can remove global sys.path mutation entirely.

## 2. Close every SQLite connection and avoid DataFrame/pyplot retention

Location: `01_expense_tracker/db.py:20-28,50-181` and `01_expense_tracker/app.py:27,52-55,78,130-131`. sqlite3 connection context managers commit/roll back but do not close connections. The old proposal closed only init_db's connection, leaving the query helpers open. The complete proposal wraps every connection context with closing. Replacing seed-time full DataFrame materialization with SQL COUNT preserves the existing return count with O(1) Python result memory. COUNT itself is not guaranteed O(1) database work. Repeated schema initialization remains a separate lifecycle cost and is not removed by this diff.

A direct matplotlib Figure avoids the pyplot global manager retaining chart figures across reruns. Callers still own any Figure they retain.

```diff
diff --git a/01_expense_tracker/db.py b/01_expense_tracker/db.py
--- a/01_expense_tracker/db.py
+++ b/01_expense_tracker/db.py
@@ -1,3 +1,4 @@
+from contextlib import closing
 import sqlite3
 from pathlib import Path
 from typing import List, Dict, Any, Optional
@@ -24,7 +25,7 @@
 
 
 def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         conn.execute(
             """
             CREATE TABLE IF NOT EXISTS expenses (
@@ -55,7 +56,7 @@
     db_path: Path = DEFAULT_DB_PATH,
 ) -> int:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         cursor = conn.execute(
             "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
             (date, category, float(amount), description),
@@ -66,7 +67,7 @@
 
 def delete_expense(expense_id: int, db_path: Path = DEFAULT_DB_PATH) -> bool:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
         conn.commit()
         return cursor.rowcount > 0
@@ -76,7 +77,7 @@
     category: str, monthly_limit: float, db_path: Path = DEFAULT_DB_PATH
 ) -> None:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         conn.execute(
             """
             INSERT INTO budgets (category, monthly_limit)
@@ -92,7 +93,7 @@
     month_prefix: Optional[str] = None, db_path: Path = DEFAULT_DB_PATH
 ) -> pd.DataFrame:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         if month_prefix:
             query = "SELECT id, date, category, amount, description FROM expenses WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC, id DESC"
             df = pd.read_sql_query(query, conn, params=(month_prefix,))
@@ -106,7 +107,7 @@
     month_prefix: Optional[str] = None, db_path: Path = DEFAULT_DB_PATH
 ) -> pd.DataFrame:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         if month_prefix:
             query = """
                 SELECT category, COUNT(*) as count, ROUND(SUM(amount), 2) as total
@@ -127,7 +128,7 @@
 
 def get_monthly_totals(db_path: Path = DEFAULT_DB_PATH) -> pd.DataFrame:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         query = """
             SELECT strftime('%Y-%m', date) as month, ROUND(SUM(amount), 2) as total
             FROM expenses
@@ -141,7 +142,7 @@
     month_prefix: str, db_path: Path = DEFAULT_DB_PATH
 ) -> List[Dict[str, Any]]:
     init_db(db_path)
-    with get_connection(db_path) as conn:
+    with closing(get_connection(db_path)) as conn, conn:
         rows = conn.execute(
             """
             SELECT b.category, b.monthly_limit, COALESCE(SUM(e.amount), 0) as spent
@@ -176,9 +177,10 @@
 
 def seed_sample_data(db_path: Path = DEFAULT_DB_PATH) -> int:
     init_db(db_path)
-    df = get_expenses_df(db_path=db_path)
-    if not df.empty:
-        return len(df)
+    with closing(get_connection(db_path)) as conn:
+        existing = int(conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0])
+    if existing:
+        return existing
     samples = [
         ("2026-09-05", "Housing & Utilities", 450.00, "Apartment rent & electricity"),
         ("2026-09-12", "Food & Dining", 85.50, "Weekly groceries"),
diff --git a/01_expense_tracker/app.py b/01_expense_tracker/app.py
--- a/01_expense_tracker/app.py
+++ b/01_expense_tracker/app.py
@@ -3,7 +3,7 @@
 from pathlib import Path
 import matplotlib
 matplotlib.use("Agg")
-import matplotlib.pyplot as plt
+from matplotlib.figure import Figure
 
 from db import (
     CATEGORIES,
@@ -24,7 +24,8 @@
     cat_df = get_category_summary(db_path=db_path)
     mon_df = get_monthly_totals(db_path=db_path)
 
-    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
+    fig = Figure(figsize=(11, 4.5))
+    axes = fig.subplots(1, 2)
     fig.patch.set_facecolor("#ffffff")
 
     if not cat_df.empty:
@@ -49,7 +50,7 @@
     else:
         axes[1].text(0.5, 0.5, "No monthly data", ha="center", va="center")
 
-    plt.tight_layout()
+    fig.tight_layout()
     if output_path:
         fig.savefig(output_path, dpi=150)
     return fig
```

Validation: Run CRUD and seeding against a temporary Windows database and unlink it without forced GC. Check commit and rollback behavior. Generate 25 charts and assert pyplot has no registered figure managers. Preserve chart contents and seed return counts.

## 3. Commit chat history only after a successful reply and close API clients

Location: `07_ai_chatbot/chatbot.py:23-39`. The current method appends a user turn before a provider request. Failed requests leave unanswered turns in persisted session history. This is a local state-integrity defect regardless of whether a provider accepts consecutive roles. The former claim of a guaranteed provider 400 response was unsupported and has been removed.

The proposal builds pending history separately, closes the per-request client even on failure, and commits the user/assistant pair together. It passes pending turns explicitly to the offline memory helper so its existing turn count and recall behavior remain intact. It does not introduce pooling. Persistent client reuse would require a separate session close/key-rotation lifecycle.

```diff
diff --git a/07_ai_chatbot/chatbot.py b/07_ai_chatbot/chatbot.py
--- a/07_ai_chatbot/chatbot.py
+++ b/07_ai_chatbot/chatbot.py
@@ -21,26 +21,25 @@
         self.history: List[Dict[str, str]] = []
 
     def send_message(self, user_message: str) -> str:
-        self.history.append({"role": "user", "content": user_message})
+        pending = [*self.history, {"role": "user", "content": user_message}]
         api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
-
         if api_key and api_key != "your_anthropic_api_key_here":
-            client = Anthropic(api_key=api_key)
-            response = client.messages.create(
-                model=self.model,
-                max_tokens=1024,
-                system=self.system_prompt,
-                messages=self.history,
-            )
-            reply = response.content[0].text
+            with Anthropic(api_key=api_key) as client:
+                response = client.messages.create(
+                    model=self.model,
+                    max_tokens=1024,
+                    system=self.system_prompt,
+                    messages=pending,
+                )
+                reply = response.content[0].text
         else:
-            reply = self._local_smart_reply(user_message)
-
-        self.history.append({"role": "assistant", "content": reply})
+            reply = self._local_smart_reply(user_message, history=pending)
+        self.history = [*pending, {"role": "assistant", "content": reply}]
         return reply
 
-    def _local_smart_reply(self, user_message: str) -> str:
-        user_turns = [m["content"] for m in self.history if m["role"] == "user"]
+    def _local_smart_reply(self, user_message: str, history=None) -> str:
+        history = self.history if history is None else history
+        user_turns = [m["content"] for m in history if m["role"] == "user"]
         lower_msg = user_message.lower()
         if "remember" in lower_msg or "my name" in lower_msg or "what did i" in lower_msg:
             prev = user_turns[:-1]
@@ -51,7 +50,7 @@
                 )
         return (
             f"[Claude SDK Ready | Turn #{len(user_turns)}] Received: \"{user_message}\". "
-            f"(Set ANTHROPIC_API_KEY in .env for live Claude API calls; conversation history has {len(self.history)} messages.)"
+            f"(Set ANTHROPIC_API_KEY in .env for live Claude API calls; conversation history has {len(history)} messages.)"
         )
 
     def clear(self) -> None:
```

Validation: Mock request failure, response-content failure and successful retry. Failed turns must leave history unchanged. Confirm context exit closes the client on each path and offline multi-turn recall retains existing outputs. Live provider delivery is a separate check.

## 4. Build quiz option widgets from the current question

Location: `03_quiz_app/app.py:45-49,68-71`. Four preallocated radio buttons fail for more than four options and leave stale choices for fewer than four. Remove the fixed preallocation and rebuild the small widget list whenever the current question changes.

```diff
diff --git a/03_quiz_app/app.py b/03_quiz_app/app.py
--- a/03_quiz_app/app.py
+++ b/03_quiz_app/app.py
@@ -43,10 +43,6 @@
     options_frame = ttk.Frame(root)
     options_frame.pack(fill="x", pady=6)
     radio_buttons = []
-    for _ in range(4):
-        rb = ttk.Radiobutton(options_frame, text="", variable=choice_var, value="")
-        rb.pack(anchor="w", pady=4)
-        radio_buttons.append(rb)
 
     ttk.Label(
         root, textvariable=feedback_var, font=("Segoe UI", 10, "italic"), wraplength=500
@@ -67,8 +63,13 @@
         )
         question_var.set(q["question"])
         choice_var.set("")
-        for idx, opt in enumerate(q["options"]):
-            radio_buttons[idx].config(text=opt, value=opt)
+        for rb in radio_buttons:
+            rb.destroy()
+        radio_buttons.clear()
+        for opt in q["options"]:
+            rb = ttk.Radiobutton(options_frame, text=opt, variable=choice_var, value=opt)
+            rb.pack(anchor="w", pady=4)
+            radio_buttons.append(rb)
 
     def on_submit():
         selected = choice_var.get()
```

Validation: Use two-option and five-option questions. Confirm widget count, empty initial selection and unchanged scoring. This needs Tkinter interaction or a faithful widget adapter; Python syntax checks alone do not establish GUI behavior.

## 5. Handle download rename events and expected filesystem races

Location: `05_file_organizer/organizer.py:91-99`. A fixed 0.1-second sleep does not prove that a producer finished writing. Partial download suffixes can be moved, while a locked or vanished file raises on the observer thread. The bounded mitigation below skips known partial suffixes, catches expected filesystem failures, and handles the final rename plus subsequent modification events. It does not establish a completion protocol for arbitrary writers, remove the observer-thread sleep, or guarantee retries if no later event arrives. A queued worker and producer completion signal remain separate concurrency work.

```diff
diff --git a/05_file_organizer/organizer.py b/05_file_organizer/organizer.py
--- a/05_file_organizer/organizer.py
+++ b/05_file_organizer/organizer.py
@@ -88,15 +88,32 @@
         super().__init__()
         self.watch_dir = Path(watch_dir)
 
+    def _organize_event_path(self, path):
+        src_path = Path(path)
+        if src_path.suffix.lower() in {".crdownload", ".part", ".tmp"}:
+            return
+        if src_path.parent.resolve() != self.watch_dir.resolve():
+            return
+        time.sleep(0.1)
+        try:
+            res = organize_single_file(src_path, self.watch_dir)
+        except OSError as exc:
+            print(f"  [Watchdog] Deferred {src_path.name}: {exc}")
+            return
+        if res:
+            print(f"  [Watchdog] Auto-moved {res['file']} -> {res['destination']}")
+
     def on_created(self, event):
-        if event.is_directory:
-            return
-        src_path = Path(event.src_path)
-        if src_path.parent.resolve() == self.watch_dir.resolve():
-            time.sleep(0.1)
-            res = organize_single_file(src_path, self.watch_dir)
-            if res:
-                print(f"  [Watchdog] Auto-moved {res['file']} -> {res['destination']}")
+        if not event.is_directory:
+            self._organize_event_path(event.src_path)
+
+    def on_modified(self, event):
+        if not event.is_directory:
+            self._organize_event_path(event.src_path)
+
+    def on_moved(self, event):
+        if not event.is_directory:
+            self._organize_event_path(event.dest_path)
 
 
 def watch_folder(folder_path: Path, duration_seconds: float | None = None) -> None:
```

Validation: Deliver created-partial, renamed-final, locked-file and vanished-file events in temporary directories. Confirm partial files remain, final rename is processed and errors leave the observer alive. Use a synthetic writer to evaluate the remaining completion race before relying on watch mode for critical data.
