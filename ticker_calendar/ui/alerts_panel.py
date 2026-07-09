import tkinter as tk
from tkinter import ttk

from ticker_calendar.services import alert_service


class AlertsPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(header, text="Alert History", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(header, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)
        ttk.Button(header, text="Check Now", command=self._check_now).pack(side=tk.RIGHT, padx=8)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("time", "rule", "ticker", "message"),
            show="headings",
        )
        self.tree.heading("time", text="Time")
        self.tree.heading("rule", text="Rule")
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("message", text="Message")
        self.tree.column("time", width=140, anchor=tk.W)
        self.tree.column("rule", width=160, anchor=tk.W)
        self.tree.column("ticker", width=70, anchor=tk.W)
        self.tree.column("message", width=360, anchor=tk.W)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_label = ttk.Label(
            self,
            text="Background monitor runs during market hours (9:30 AM – 4:00 PM ET)",
            font=("Segoe UI", 8, "italic"),
        )
        self.status_label.pack(pady=8)

        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for record in alert_service.get_recent_alerts():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record.created_at,
                    record.rule_id,
                    record.ticker,
                    record.message,
                ),
            )

    def _check_now(self):
        fired = alert_service.AlertMonitor().check_now()
        self.refresh()
        self.status_label.configure(
            text=f"Manual check complete — {len(fired)} new alert(s)"
        )

    def add_live_alert(self, candidate):
        self.tree.insert(
            "0",
            tk.END,
            values=(
                "just now",
                candidate.rule_name,
                candidate.ticker,
                candidate.message,
            ),
        )
