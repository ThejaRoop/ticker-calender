# Alert Rules

Human-readable reference for all automated buy-call alerts.  
Program constants live in `ticker_calendar/config/alert_rules.py` and should stay in sync with this file.

**Market timezone:** US Eastern (`America/New_York`)  
**"Down" definition:** current price is below today's opening price (`current < open`).

---

## Rule 1 — Earnings Today (intraday dip)

| Field | Value |
|-------|-------|
| **ID** | `earnings_today` |
| **When** | Today is a scheduled **earning date** for a ticker |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Price condition** | Stock is down from open (`current < open`) |
| **Alert** | "There is a chance to buy call for {TICKER}" |

Only applies to source earning dates (not auto-generated 90-day recurrence entries).

---

## Rule 2 — Earnings Next Week (prior Friday setup)

| Field | Value |
|-------|-------|
| **ID** | `earnings_next_week` |
| **When** | Today is **Friday** and a ticker has an earning date in **next calendar week** (Mon–Sun) |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Price condition** | None (setup alert before the week) |
| **Alert** | "There is a chance to buy call for {TICKER} (earnings next week)" |

"Next week" = the Monday–Sunday period starting the Monday after this Friday.

---

## Rule 3 — Earnings Tomorrow (2 PM dip)

| Field | Value |
|-------|-------|
| **ID** | `earnings_tomorrow` |
| **When** | A ticker has an earning date **tomorrow** |
| **Time window** | 2:00 PM ET |
| **Price condition** | Stock is down from open at the 2:00 PM check (`current < open`) |
| **Alert** | "There is a chance to buy call for {TICKER} (earnings tomorrow)" |

This helps catch names that look like they may rebound by the close if earnings are scheduled for the next trading day.

---

## Rule 4 — Popular stocks weekday dip (Mon–Wed)

| Field | Value |
|-------|-------|
| **ID** | `popular_weekday` |
| **When** | Today is **Monday, Tuesday, or Wednesday** |
| **Time window** | 10:30 AM ET (checked within 10:30–10:35 AM) |
| **Tickers** | Popular stocks list (manageable in app) |
| **Price condition** | Stock is down from open (`current < open`) |
| **Alert** | "There is a chance to buy call for {TICKER}" |

---

## Rule 5 — Popular stocks list (management)

| Field | Value |
|-------|-------|
| **ID** | `popular_list` |
| **Purpose** | CRUD for the popular tickers used by Rules 3 and 5 |
| **Default list** | See `ticker_calendar/config/defaults.py` |

---

## Rule 6 — Popular stocks Friday dip

| Field | Value |
|-------|-------|
| **ID** | `popular_friday` |
| **When** | Today is a **normal Friday** (weekday Friday, US market open day) |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Tickers** | Popular stocks list |
| **Price condition** | Stock is down from open (`current < open`) |
| **Alert** | "There is a chance to buy call for {TICKER}" |

---

## Rule 7 — Thursday Shakeout

| Field | Value |
|-------|-------|
| **ID** | `thursday_shakeout` |
| **When** | Thursday |
| **Time window** | 11:00 AM ET |
| **Tickers** | Popular stocks list |
| **Price condition** | Current price is down more than 1.5% from the previous close |
| **Alert** | "Thursday liquidity discount on {TICKER}" |

---

## Rule 8 — End-of-Day Reversal

| Field | Value |
|-------|-------|
| **ID** | `eod_reversal` |
| **When** | Monday–Thursday |
| **Time window** | 3:30 PM ET |
| **Tickers** | Popular stocks list |
| **Price condition** | Stock is down from open but still above the day's low |
| **Alert** | "Closing reversal setup for {TICKER}" |

---

## Rule 9 — Gap-Fill Momentum

| Field | Value |
|-------|-------|
| **ID** | `gap_fill_trade` |
| **When** | Daily |
| **Time window** | 10:00 AM – 10:30 AM ET |
| **Tickers** | Popular stocks list |
| **Price condition** | Open is below the previous close and price is now above the opening-range high |
| **Alert** | "Gap-fill momentum initiating for {TICKER}" |

---

## Alert behavior

- Each rule fires **at most once per ticker per day** (deduplicated in the database).
- Alerts appear in the **Alerts** panel and as desktop pop-ups while the app is running.
- The **Ubuntu server** (`run_server.py serve`) fires checks at exact times via APScheduler (no polling).
- The desktop UI background monitor polls every **30 seconds** during US market hours (9:30 AM – 4:00 PM ET).
- Live prices are fetched via **Yahoo Finance** (`yfinance`) only when a check runs.
