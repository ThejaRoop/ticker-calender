import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk

from ticker_calendar.rules.evaluator import AlertCandidate
from ticker_calendar.services import alert_service
from ticker_calendar.ui.alerts_panel import AlertsPanel
from ticker_calendar.ui.calendar_view import CalendarView
from ticker_calendar.ui.popular_dialog import PopularTickersDialog
from ticker_calendar.ui.ticker_dialog import TickerDialog

RULES_PATH = Path(__file__).resolve().parent.parent.parent / "ALERT_RULES.md"


class CalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ticker Calendar")
        self.geometry("1000x700")
        self.minsize(900, 600)

        self._build_menu()
        self._build_notebook()

        self.alert_monitor = alert_service.AlertMonitor(on_alert=self._on_alert)
        self.alert_monitor.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=file_menu)
        file_menu.add_command(label="Popular Tickers...", command=self._open_popular)
        file_menu.add_separator()
        file_menu.add_command(label="View Alert Rules", command=self._open_rules)

        alerts_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Alerts", menu=alerts_menu)
        alerts_menu.add_command(label="Check Now", command=self._check_alerts_now)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        calendar_tab = ttk.Frame(self.notebook)
        self.notebook.add(calendar_tab, text="Calendar")

        self.calendar_view = CalendarView(calendar_tab, on_open_day=self._open_day)
        self.calendar_view.pack(fill=tk.BOTH, expand=True)

        alerts_tab = ttk.Frame(self.notebook)
        self.notebook.add(alerts_tab, text="Alerts")
        self.alerts_panel = AlertsPanel(alerts_tab)
        self.alerts_panel.pack(fill=tk.BOTH, expand=True)

    def _open_day(self, entry_date: date):
        TickerDialog(self, entry_date, on_change=self.calendar_view.refresh)

    def _open_popular(self):
        PopularTickersDialog(self)

    def _open_rules(self):
        if not RULES_PATH.exists():
            messagebox.showinfo("Rules", "ALERT_RULES.md not found.", parent=self)
            return
        RulesViewer(self, RULES_PATH.read_text(encoding="utf-8"))

    def _check_alerts_now(self):
        self.notebook.select(1)
        self.alerts_panel._check_now()

    def _on_alert(self, candidate: AlertCandidate):
        self.after(0, lambda: self._show_alert(candidate))

    def _show_alert(self, candidate: AlertCandidate):
        self.alerts_panel.add_live_alert(candidate)
        messagebox.showinfo(
            "Buy Call Alert",
            f"{candidate.message}\n\nRule: {candidate.rule_name}",
            parent=self,
        )

    def _on_close(self):
        self.alert_monitor.stop()
        self.destroy()


class RulesViewer(tk.Toplevel):
    def __init__(self, parent, content: str):
        super().__init__(parent)
        self.title("Alert Rules")
        self.geometry("640x520")
        self.transient(parent)

        text = tk.Text(self, wrap=tk.WORD, font=("Consolas", 10), padx=12, pady=12)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", content)
        text.configure(state=tk.DISABLED)

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=8)


def run():
    from ticker_calendar.db.connection import init_db

    init_db()
    app = CalendarApp()
    app.mainloop()
