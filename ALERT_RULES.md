# Alert Rules (Database & Time-Only)

Human-readable reference for all automated buy-call alerts. Program constants live in `ticker_calendar/config/alert_rules.py`.

**Market timezone:** US Eastern (`America/New_York`)  
**Core principle:** Alerts fire based strictly on calendar events and lists stored in the local database matching the current time and day. No external price APIs are used.

---

## Earnings-Based Rules

### Rule 1 — Earnings Today

| Field | Value |
|-------|-------|
| **ID** | `earnings_today` |
| **When** | Today is a scheduled **earning date** for a ticker in the local database |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Alert** | "There is a chance to buy call for {TICKER}" |

Only applies to source earning dates (not auto-generated 90-day recurrence entries).

---

### Rule 2 — Earnings Next Week (Prior Friday Setup)

| Field | Value |
|-------|-------|
| **ID** | `earnings_next_week` |
| **When** | Today is **Friday** and a ticker has an earning date in **next calendar week** (Mon–Sun) per local DB |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Alert** | "There is a chance to buy call for {TICKER} (earnings next week)" |

"Next week" = the Monday–Sunday period starting the Monday after this Friday.

---

### Rule 3 — Earnings Tomorrow

| Field | Value |
|-------|-------|
| **ID** | `earnings_tomorrow` |
| **When** | A ticker has an earning date **tomorrow** per local DB |
| **Time window** | 2:00 PM ET |
| **Alert** | "There is a chance to buy call for {TICKER} (earnings tomorrow)" |

---

### Rule 4 — Earnings Day Morning Matrix

| Field | Value |
|-------|-------|
| **ID** | `earnings_day_morning_matrix` |
| **When** | Today is an **earning date** for a ticker in the local database |
| **Time window** | 9:45 AM – 11:00 AM ET |
| **Alert** | "Earnings buy window open for {TICKER}" |

---

## Popular Ticker Rules

### Rule 5 — Popular Stocks Weekday Watch

| Field | Value |
|-------|-------|
| **ID** | `popular_weekday` |
| **When** | Today is **Monday, Tuesday, or Wednesday** |
| **Time window** | 10:30 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "There is a chance to buy call for {TICKER}" |

---

### Rule 6 — Popular Stocks Friday Watch

| Field | Value |
|-------|-------|
| **ID** | `popular_friday` |
| **When** | Today is a **normal Friday** (weekday Friday, US market open day) |
| **Time window** | 10:00 AM – 10:45 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "There is a chance to buy call for {TICKER}" |

---

### Rule 7 — Thursday Liquidity Setup

| Field | Value |
|-------|-------|
| **ID** | `thursday_shakeout` |
| **When** | Thursday |
| **Time window** | 11:00 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Thursday liquidity setup on {TICKER}" |

---

### Rule 8 — End-of-Day Check

| Field | Value |
|-------|-------|
| **ID** | `eod_reversal` |
| **When** | Monday–Thursday |
| **Time window** | 3:30 PM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Closing schedule check for {TICKER}" |

---

### Rule 9 — Morning Momentum Check

| Field | Value |
|-------|-------|
| **ID** | `gap_fill_trade` |
| **When** | Daily |
| **Time window** | 10:00 AM – 10:30 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Morning momentum setup initiating for {TICKER}" |

---

### Rule 10 — IV Crush Window

| Field | Value |
|-------|-------|
| **ID** | `iv_crush` |
| **When** | Monday–Friday |
| **Time window** | 9:45 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "9:45 AM IV Crush window open for {TICKER}" |

---

## Day-Specific Magic Hour Rules

### Rule 11 — Monday Gap Fill

| Field | Value |
|-------|-------|
| **ID** | `monday_gap_fill` |
| **When** | Monday |
| **Time window** | 10:15 AM – 11:30 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Monday Gap Fill window active for {TICKER}" |

---

### Rule 12 — Tuesday High/Low Window

| Field | Value |
|-------|-------|
| **ID** | `tuesday_high_low` |
| **When** | Tuesday |
| **Time window** | 9:30 AM – 10:30 AM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Tuesday High/Low window active for {TICKER}" |

---

### Rule 13 — Wednesday Mid-Week Reversal

| Field | Value |
|-------|-------|
| **ID** | `wednesday_midweek` |
| **When** | Wednesday |
| **Time window** | 2:00 PM – 4:00 PM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Wednesday Mid-Week Reversal window for {TICKER}" |

---

### Rule 14 — Friday Gamma Squeeze

| Field | Value |
|-------|-------|
| **ID** | `friday_gamma_squeeze` |
| **When** | Friday |
| **Time window** | 2:30 PM – 4:50 PM ET |
| **Tickers** | Popular stocks list stored locally |
| **Alert** | "Friday Gamma Squeeze window active for {TICKER}" |

---

## Alert Behavior

- Each rule fires **at most once per ticker per day** (deduplicated in the database).
- Alerts appear in the **Alerts** panel and as desktop pop-ups while the app is running.
- The **Ubuntu server** (`run_server.py serve`) fires checks at exact times via APScheduler based entirely on local SQLite database records and system clock time.
- **No network requests or external price APIs are utilized.**