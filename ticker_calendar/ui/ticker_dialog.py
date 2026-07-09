import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk

from ticker_calendar.config.settings import CALENDAR_END, CALENDAR_START
from ticker_calendar.db import tickers as tickers_db
from ticker_calendar.services import calendar_service


class TickerDialog(tk.Toplevel):
    def __init__(self, parent, entry_date: date, on_change):
        super().__init__(parent)
        self.entry_date = entry_date
        self.on_change = on_change
        self.title(f"Tickers — {entry_date.strftime('%B %d, %Y')}")
        self.geometry("420x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        header = ttk.Label(
            self,
            text=entry_date.strftime("%A, %B %d, %Y"),
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(pady=(12, 8))

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("ticker", "type"),
            show="headings",
            height=8,
        )
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("type", text="Type")
        self.tree.column("ticker", width=120, anchor=tk.W)
        self.tree.column("type", width=200, anchor=tk.W)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)

        ttk.Button(btn_frame, text="Add", command=self._add).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Edit", command=self._edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Delete", command=self._delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=4)

        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for entry in calendar_service.get_day_entries(self.entry_date):
            if entry.entry_date == entry.source_date:
                entry_type = "Earning date (source)"
            else:
                days = (entry.entry_date - entry.source_date).days
                entry_type = f"Auto (+{days}d from {entry.source_date.strftime('%m/%d/%y')})"
            self.tree.insert("", tk.END, iid=str(entry.id), values=(entry.ticker, entry_type))

    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def _add(self):
        ticker = simpledialog.askstring("Add Ticker", "Enter ticker symbol:", parent=self)
        if not ticker:
            return

        if self.entry_date < CALENDAR_START or self.entry_date > CALENDAR_END:
            messagebox.showerror(
                "Out of range",
                f"Dates must be between {CALENDAR_START} and {CALENDAR_END}.",
                parent=self,
            )
            return

        added, skipped = calendar_service.add_ticker_with_recurrence(ticker, self.entry_date)
        if not added:
            messagebox.showwarning(
                "Duplicate",
                f"{ticker.upper()} already exists on all recurrence dates.",
                parent=self,
            )
            return

        msg = f"Added {ticker.upper()} on {len(added)} date(s) (every 90 days)."
        if skipped:
            msg += f"\n{len(skipped)} date(s) skipped (already existed)."
        messagebox.showinfo("Added", msg, parent=self)
        self._refresh()
        self.on_change()

    def _edit(self):
        entry_id = self._selected_id()
        if entry_id is None:
            messagebox.showinfo("Select", "Select a ticker to edit.", parent=self)
            return

        entry = tickers_db.get_entry(entry_id)
        if not entry:
            return

        new_ticker = simpledialog.askstring(
            "Edit Ticker",
            "New ticker symbol:",
            initialvalue=entry.ticker,
            parent=self,
        )
        if not new_ticker or new_ticker.upper() == entry.ticker:
            return

        updated = calendar_service.update_ticker(entry_id, new_ticker)
        if not updated:
            messagebox.showerror(
                "Error",
                f"Could not rename to {new_ticker.upper()} (duplicate on this date?).",
                parent=self,
            )
            return

        self._refresh()
        self.on_change()

    def _delete(self):
        entry_id = self._selected_id()
        if entry_id is None:
            messagebox.showinfo("Select", "Select a ticker to delete.", parent=self)
            return

        entry = tickers_db.get_entry(entry_id)
        if not entry:
            return

        is_source = entry.entry_date == entry.source_date
        if is_source:
            answer = messagebox.askyesnocancel(
                "Delete",
                f"Delete {entry.ticker} on this date only?\n\n"
                "Yes = this date only\n"
                "No = entire 90-day series\n"
                "Cancel = abort",
                parent=self,
            )
            if answer is None:
                return
            delete_series = not answer
        else:
            if not messagebox.askyesno(
                "Delete",
                f"Delete {entry.ticker} on {entry.entry_date.strftime('%m/%d/%Y')}?",
                parent=self,
            ):
                return
            delete_series = False

        removed = calendar_service.delete_ticker(entry_id, delete_series=delete_series)
        if removed:
            self._refresh()
            self.on_change()
        else:
            messagebox.showerror("Error", "Could not delete ticker.", parent=self)
