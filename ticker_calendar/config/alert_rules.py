from datetime import time

# Mirrors ALERT_RULES.md — keep in sync when editing rules.

MARKET_TIMEZONE = "America/New_York"

MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

RULE_EARNINGS_TODAY = {
    "id": "earnings_today",
    "name": "Earnings Today",
    "requires_down": True,
}

RULE_EARNINGS_NEXT_WEEK = {
    "id": "earnings_next_week",
    "name": "Earnings Next Week (Prior Friday)",
    "requires_down": False,
}

RULE_POPULAR_WEEKDAY = {
    "id": "popular_weekday",
    "name": "Popular Stocks Weekday Dip",
    "weekdays": {0, 1, 2},  # Mon, Tue, Wed
    "requires_down": True,
}

RULE_POPULAR_FRIDAY = {
    "id": "popular_friday",
    "name": "Popular Stocks Friday Dip",
    "weekdays": {4},  # Friday
    "requires_down": True,
}

RULES_BY_ID = {
    RULE_EARNINGS_TODAY["id"]: RULE_EARNINGS_TODAY,
    RULE_EARNINGS_NEXT_WEEK["id"]: RULE_EARNINGS_NEXT_WEEK,
    RULE_POPULAR_WEEKDAY["id"]: RULE_POPULAR_WEEKDAY,
    RULE_POPULAR_FRIDAY["id"]: RULE_POPULAR_FRIDAY,
}

ALERT_MESSAGE = "There is a chance to buy call for {ticker}"
ALERT_MESSAGE_NEXT_WEEK = "There is a chance to buy call for {ticker} (earnings next week)"

# Exact scheduled fire times (ET). Scheduler runs each job at these times only.
# weekdays: mon,tue,wed,thu,fri | fri | mon,tue,wed
SCHEDULED_CHECKS = [
    {
        "rule_id": "earnings_today",
        "times": ["10:00", "10:15", "10:30", "10:45"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "earnings_next_week",
        "times": ["10:00"],
        "weekdays": "fri",
    },
    {
        "rule_id": "popular_weekday",
        "times": ["10:30"],
        "weekdays": "mon,tue,wed",
    },
    {
        "rule_id": "popular_friday",
        "times": ["10:00", "10:15", "10:30", "10:45"],
        "weekdays": "fri",
    },
]

# APScheduler: seconds to wait before treating a missed job as stale
MISFIRE_GRACE_SECONDS = 300

# Desktop UI background monitor (local app only — server uses SCHEDULED_CHECKS)
POLL_INTERVAL_SECONDS = 30
