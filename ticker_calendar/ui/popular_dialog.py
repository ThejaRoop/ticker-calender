import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from ticker_calendar.services import popular_service


class PopularTickersDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Popular Tickers")
        self.geometry("360x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        ttk.Label(
            self,
            text="Popular stocks used by weekday & Friday alert rules",
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(12, 8))

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)

        ttk.Button(btn_frame, text="Add", command=self._add).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Delete", command=self._delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=4)

        self.count_label = ttk.Label(self, text="", font=("Segoe UI", 8))
        self.count_label.pack(pady=(0, 8))

        self._refresh()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        items = popular_service.list_popular()
        for item in items:
            self.listbox.insert(tk.END, item.ticker)
        self.count_label.configure(text=f"{len(items)} tickers")

    def _add(self):
        ticker = simpledialog.askstring("Add Popular Ticker", "Enter ticker symbol:", parent=self)
        if not ticker:
            return
        result = popular_service.add_popular(ticker)
        if not result:
            messagebox.showwarning("Duplicate", f"{ticker.upper()} is already in the list.", parent=self)
            return
        self._refresh()

    def _delete(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Select", "Select a ticker to delete.", parent=self)
            return
        ticker = self.listbox.get(selection[0])
        if messagebox.askyesno("Delete", f"Remove {ticker} from popular list?", parent=self):
            popular_service.remove_popular(ticker)
            self._refresh()
