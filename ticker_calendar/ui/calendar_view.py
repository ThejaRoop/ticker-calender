import calendar
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from ticker_calendar.config.settings import CALENDAR_END, CALENDAR_START, TODAY
from ticker_calendar.services import calendar_service


class CalendarView(ttk.Frame):
    def __init__(self, parent, on_open_day):
        super().__init__(parent)
        self.on_open_day = on_open_day
        self.current_year = TODAY.year
        self.current_month = TODAY.month
        self.day_buttons: dict[date, tk.Button] = {}

        self._build_header()
        self._build_calendar_grid()
        self._build_footer()
        self.refresh()

    def _build_header(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=12, pady=10)

        ttk.Button(header, text="◀", width=3, command=self._prev_month).pack(side=tk.LEFT)
        self.month_label = ttk.Label(header, text="", font=("Segoe UI", 14, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(header, text="▶", width=3, command=self._next_month).pack(side=tk.RIGHT)
        ttk.Button(header, text="Today", command=self._go_today).pack(side=tk.RIGHT, padx=8)

    def _build_calendar_grid(self):
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, name in enumerate(weekdays):
            lbl = ttk.Label(
                self.grid_frame,
                text=name,
                anchor=tk.CENTER,
                font=("Segoe UI", 9, "bold"),
            )
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for row in range(1, 7):
            for col in range(7):
                btn = tk.Button(
                    self.grid_frame,
                    text="",
                    justify=tk.LEFT,
                    anchor=tk.NW,
                    relief=tk.FLAT,
                    bg="#ffffff",
                    activebackground="#e8f0fe",
                    font=("Segoe UI", 9),
                    wraplength=110,
                    command=lambda: None,
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                btn.bind("<Enter>", lambda e, b=btn: self._on_day_hover(b, True))
                btn.bind("<Leave>", lambda e, b=btn: self._on_day_hover(b, False))

        for col in range(7):
            self.grid_frame.columnconfigure(col, weight=1, uniform="day")
        for row in range(1, 7):
            self.grid_frame.rowconfigure(row, weight=1, uniform="week")

    def _build_footer(self):
        footer = ttk.Frame(self)
        footer.pack(fill=tk.X, padx=12, pady=8)

        range_text = (
            f"Calendar range: {CALENDAR_START.strftime('%b %Y')} — "
            f"{CALENDAR_END.strftime('%b %Y')}  |  "
            f"Tickers auto-repeat every 90 days from earning date"
        )
        ttk.Label(footer, text=range_text, font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Label(
            footer,
            text="Click a day to manage tickers",
            font=("Segoe UI", 8, "italic"),
        ).pack(side=tk.RIGHT)

    def _on_day_hover(self, btn: tk.Button, entering: bool):
        if btn.cget("state") == tk.DISABLED:
            return
        btn.configure(relief=tk.RAISED if entering else tk.FLAT)

    def _can_navigate(self, year: int, month: int) -> bool:
        first = date(year, month, 1)
        if month == 12:
            last = date(year + 1, 1, 1)
        else:
            last = date(year, month + 1, 1)
        month_end = last - timedelta(days=1)
        return month_end >= CALENDAR_START.replace(day=1) and first <= CALENDAR_END

    def _prev_month(self):
        if self.current_month == 1:
            year, month = self.current_year - 1, 12
        else:
            year, month = self.current_year, self.current_month - 1
        if self._can_navigate(year, month):
            self.current_year, self.current_month = year, month
            self.refresh()

    def _next_month(self):
        if self.current_month == 12:
            year, month = self.current_year + 1, 1
        else:
            year, month = self.current_year, self.current_month + 1
        if self._can_navigate(year, month):
            self.current_year, self.current_month = year, month
            self.refresh()

    def _go_today(self):
        self.current_year = TODAY.year
        self.current_month = TODAY.month
        self.refresh()

    def refresh(self):
        self.month_label.configure(
            text=date(self.current_year, self.current_month, 1).strftime("%B %Y")
        )
        self.day_buttons.clear()

        month_data = calendar_service.get_month_data(self.current_year, self.current_month)
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        btn_index = 0
        buttons = [
            self.grid_frame.grid_slaves(row=r, column=c)[0]
            for r in range(1, 7)
            for c in range(7)
        ]

        for week in weeks:
            for day in week:
                btn = buttons[btn_index]
                btn_index += 1
                btn.configure(state=tk.NORMAL, command=lambda: None)

                if day == 0:
                    btn.configure(
                        text="",
                        bg="#f5f5f5",
                        fg="#999999",
                        state=tk.DISABLED,
                        relief=tk.FLAT,
                    )
                    continue

                entry_date = date(self.current_year, self.current_month, day)
                in_range = CALENDAR_START <= entry_date <= CALENDAR_END
                entries = month_data.get(entry_date, [])

                lines = [str(day)]
                for entry in entries[:4]:
                    lines.append(entry.ticker)
                if len(entries) > 4:
                    lines.append(f"+{len(entries) - 4} more")

                if entry_date == TODAY:
                    bg = "#fff3cd"
                elif not in_range:
                    bg = "#f0f0f0"
                else:
                    bg = "#ffffff"

                btn.configure(
                    text="\n".join(lines),
                    bg=bg,
                    fg="#333333" if in_range else "#aaaaaa",
                    state=tk.NORMAL if in_range else tk.DISABLED,
                    relief=tk.FLAT,
                )

                if in_range:
                    self.day_buttons[entry_date] = btn
                    btn.configure(command=lambda d=entry_date: self.on_open_day(d))
