# Alert Rules (Database & Time-Only)

Human-readable reference for all automated buy-call alerts. Program constants live in `ticker_calendar/config/alert_rules.py`.

**Market timezone:** US Eastern (`America/New_York`)  
**Core principle:** Alerts fire based strictly on calendar events and lists stored in the local database matching the current time and day. No external price APIs are used.

---

## Section 1: Earnings-Based Rules

### Rule 1 — Earnings Today
| Field | Specification |
|-------|---------------|
| **Rule ID** | `earnings_today` |
| **Trigger Condition** | The current calendar date matches a scheduled earnings date for a ticker in the local database |
| **Time Window** | 10:00 AM – 10:45 AM ET |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "There is a chance to buy call for {TICKER}" |

### Rule 2 — Earnings Next Week (Prior Friday Setup)
| Field | Specification |
|-------|---------------|
| **Rule ID** | `earnings_next_week` |
| **Trigger Condition** | Today is Friday, and a ticker has a recorded earnings date falling within the next calendar week (Monday–Sunday) per the local database |
| **Time Window** | 10:00 AM – 10:45 AM ET |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "There is a chance to buy call for {TICKER} (earnings next week)" |
| **Definition Note** | "Next week" strictly designates the Monday through Sunday period immediately following the current Friday. |

### Rule 3 — Earnings Tomorrow
| Field | Specification |
|-------|---------------|
| **Rule ID** | `earnings_tomorrow` |
| **Trigger Condition** | A ticker has a recorded earnings date tomorrow according to the local database |
| **Time Window** | 2:00 PM ET (Exact trigger point) |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "There is a chance to buy call for {TICKER} (earnings tomorrow)" |

### Rule 4 — Earnings Day Morning Matrix
| Field | Specification |
|-------|---------------|
| **Rule ID** | `earnings_day_morning_matrix` |
| **Trigger Condition** | Today is an active earnings date for a ticker in the local database |
| **Time Window** | 9:45 AM – 11:00 AM ET |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "Earnings buy window open for {TICKER}" |

### Rule 6 — Post-Earnings Momentum Window (Day +1)
| Field | Specification |
|-------|---------------|
| **Rule ID** | `post_earnings_momentum` |
| **Trigger Condition** | Today is the calendar day immediately following a recorded earnings date for a ticker in the local database |
| **Time Window** | 9:45 AM – 10:30 AM ET |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "Post-earnings volatility window active for {TICKER}" |
| **Strategic Rationale** | Captures immediate market digestion and continuation momentum right after the dust settles from the prior day's earnings release. |

### Rule 7 — Mid-Week Earnings Lookahead (Wednesday Setup)
| Field | Specification |
|-------|---------------|
| **Rule ID** | `midweek_earnings_setup` |
| **Trigger Condition** | Today is Wednesday, and a ticker has a recorded earnings date scheduled for Thursday or Friday of the same week |
| **Time Window** | 1:00 PM – 2:00 PM ET |
| **Target Scope** | All valid database tickers meeting the calendar condition |
| **Alert Payload** | "Mid-week pre-earnings setup for {TICKER} (reporting soon)" |
| **Strategic Rationale** | Captures institutional positioning that occurs mid-week ahead of late-week announcements. |

---

## Section 2: Market Structure & Watchlist Rules

### Rule 5 — Popular Stocks Friday Watch
| Field | Specification |
|-------|---------------|
| **Rule ID** | `popular_friday` |
| **Trigger Condition** | Today is a standard trading Friday (weekday Friday, US market open day) |
| **Time Window** | 10:00 AM – 10:45 AM ET |
| **Target Scope** | Restricted specifically to the curated popular stocks watchlist: MSFT, GOOGL, NVDA, SPY |
| **Alert Payload** | "There is a chance to buy call for {TICKER}" |

### Rule 8 — Monthly Options Expiration (OPEX) Friday Watch
| Field | Specification |
|-------|---------------|
| **Rule ID** | `monthly_opex_friday` |
| **Trigger Condition** | Today is the third Friday of the calendar month (Standard Monthly OPEX) and a US market open day |
| **Time Window** | 10:30 AM – 11:30 AM ET |
| **Target Scope** | Restricted to core high-liquidity database tickers or watchlist assets |
| **Alert Payload** | "Monthly OPEX volatility window open for {TICKER}" |
| **Strategic Rationale** | Leverages predictable structural gamma shifts and heavy volume dynamics tied to monthly options expiration cycles. |

### Rule 9 — Month-End Institutional Flow Setup
| Field | Specification |
|-------|---------------|
| **Rule ID** | `quarter_end_rebalance` |
| **Trigger Condition** | Today is the last trading day of the calendar month per the local database calendar |
| **Time Window** | 3:00 PM – 3:45 PM ET |
| **Target Scope** | Curated index proxies and major large-cap database entries (e.g., SPY, MSFT, NVDA) |
| **Alert Payload** | "Month-end rebalancing flow window active for {TICKER}" |

---

## Alert Behavior

- Alerts appear in the **Alerts** panel and as desktop pop-ups while the app is running.
- The **Ubuntu server** (`run_server.py serve`) fires checks at exact times via APScheduler based entirely on local SQLite database records and system clock time.
- **No network requests or external price APIs are utilized.**