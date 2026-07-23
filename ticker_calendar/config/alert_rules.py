from datetime import time

# Mirrors ALERT_RULES.md — keep in sync when editing rules.

MARKET_TIMEZONE = "America/New_York"

MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

RULE_EARNINGS_TODAY = {
    "id": "earnings_today",
    "name": "Earnings Today",
    "requires_down": False,
}

RULE_EARNINGS_NEXT_WEEK = {
    "id": "earnings_next_week",
    "name": "Earnings Next Week (Prior Friday)",
    "requires_down": False,
}

RULE_EARNINGS_TOMORROW = {
    "id": "earnings_tomorrow",
    "name": "Earnings Tomorrow (2 PM Dip)",
    "requires_down": False,
}

RULE_EARNINGS_DAY_MORNING_MATRIX = {
    "id": "earnings_day_morning_matrix",
    "name": "Earnings Day Morning Matrix",
    "requires_down": False,
}

RULE_POPULAR_WEEKDAY = {
    "id": "popular_weekday",
    "name": "Popular Stocks Weekday Dip",
    "weekdays": {0, 1, 2},  # Mon, Tue, Wed
    "requires_down": False,
}

RULE_POPULAR_FRIDAY = {
    "id": "popular_friday",
    "name": "Popular Stocks Friday Dip",
    "weekdays": {4},  # Friday
    "requires_down": False,
}

RULE_THURSDAY_SHAKEOUT = {
    "id": "thursday_shakeout",
    "name": "Thursday Shakeout",
    "weekdays": {3},  # Thursday
    "requires_down": False,
}

RULE_EOD_REVERSAL = {
    "id": "eod_reversal",
    "name": "End of Day Reversal",
    "weekdays": {0, 1, 2, 3},  # Mon-Thu
    "requires_down": False,
}

RULE_GAP_FILL_TRADE = {
    "id": "gap_fill_trade",
    "name": "Gap Fill Momentum",
    "requires_down": False,
}

RULE_IV_CRUSH = {
    "id": "iv_crush",
    "name": "IV Crush Window",
    "weekdays": {0, 1, 2, 3, 4},  # Mon-Fri
    "requires_down": False,
}

RULE_MONDAY_GAP_FILL = {
    "id": "monday_gap_fill",
    "name": "Monday Gap Fill",
    "weekdays": {0},  # Monday
    "requires_down": False,
}

RULE_TUESDAY_HIGH_LOW = {
    "id": "tuesday_high_low",
    "name": "Tuesday High/Low Window",
    "weekdays": {1},  # Tuesday
    "requires_down": False,
}

RULE_WEDNESDAY_MIDWEEK = {
    "id": "wednesday_midweek",
    "name": "Wednesday Mid-Week Reversal",
    "weekdays": {2},  # Wednesday
    "requires_down": False,
}

RULE_FRIDAY_GAMMA_SQUEEZE = {
    "id": "friday_gamma_squeeze",
    "name": "Friday Gamma Squeeze",
    "weekdays": {4},  # Friday
    "requires_down": False,
}

RULES_BY_ID = {
    RULE_EARNINGS_TODAY["id"]: RULE_EARNINGS_TODAY,
    RULE_EARNINGS_NEXT_WEEK["id"]: RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TOMORROW["id"]: RULE_EARNINGS_TOMORROW,
    RULE_EARNINGS_DAY_MORNING_MATRIX["id"]: RULE_EARNINGS_DAY_MORNING_MATRIX,
    RULE_POPULAR_WEEKDAY["id"]: RULE_POPULAR_WEEKDAY,
    RULE_POPULAR_FRIDAY["id"]: RULE_POPULAR_FRIDAY,
    RULE_THURSDAY_SHAKEOUT["id"]: RULE_THURSDAY_SHAKEOUT,
    RULE_EOD_REVERSAL["id"]: RULE_EOD_REVERSAL,
    RULE_GAP_FILL_TRADE["id"]: RULE_GAP_FILL_TRADE,
    RULE_IV_CRUSH["id"]: RULE_IV_CRUSH,
    RULE_MONDAY_GAP_FILL["id"]: RULE_MONDAY_GAP_FILL,
    RULE_TUESDAY_HIGH_LOW["id"]: RULE_TUESDAY_HIGH_LOW,
    RULE_WEDNESDAY_MIDWEEK["id"]: RULE_WEDNESDAY_MIDWEEK,
    RULE_FRIDAY_GAMMA_SQUEEZE["id"]: RULE_FRIDAY_GAMMA_SQUEEZE,
}

ALERT_MESSAGE = "There is a chance to buy call for {ticker}"
ALERT_MESSAGE_NEXT_WEEK = "There is a chance to buy call for {ticker} (earnings next week)"
ALERT_MESSAGE_TOMORROW = "There is a chance to buy call for {ticker} (earnings tomorrow)"
ALERT_MESSAGE_THURSDAY_SHAKEOUT = "Thursday liquidity setup on {ticker}"
ALERT_MESSAGE_EOD_REVERSAL = "Closing schedule check for {ticker}"
ALERT_MESSAGE_GAP_FILL = "Morning momentum setup initiating for {ticker}"
ALERT_MESSAGE_IV_CRUSH = "9:45 AM IV Crush window open for {ticker}"
ALERT_MESSAGE_MONDAY_GAP_FILL = "Monday Gap Fill window active for {ticker}"
ALERT_MESSAGE_TUESDAY_HIGH_LOW = "Tuesday High/Low window active for {ticker}"
ALERT_MESSAGE_WEDNESDAY_MIDWEEK = "Wednesday Mid-Week Reversal window for {ticker}"
ALERT_MESSAGE_FRIDAY_GAMMA_SQUEEZE = "Friday Gamma Squeeze window active for {ticker}"
ALERT_MESSAGE_EARNINGS_MATRIX = "Earnings buy window open for {ticker}"

# Exact scheduled fire times (ET). Scheduler runs each job at these times only.
SCHEDULED_CHECKS = [
    {
        "rule_id": "earnings_today",
        "times": ["10:00", "10:15", "10:30", "10:45"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "earnings_next_week",
        "times": ["10:00", "10:15", "10:30", "10:45"],
        "weekdays": "fri",
    },
    {
        "rule_id": "earnings_tomorrow",
        "times": ["14:00"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "earnings_day_morning_matrix",
        "times": ["09:45", "10:00", "10:15", "10:30", "10:45", "11:00"],
        "weekdays": "mon,tue,wed,thu,fri",
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
    {
        "rule_id": "thursday_shakeout",
        "times": ["11:00"],
        "weekdays": "thu",
    },
    {
        "rule_id": "eod_reversal",
        "times": ["15:30"],
        "weekdays": "mon,tue,wed,thu",
    },
    {
        "rule_id": "gap_fill_trade",
        "times": ["10:00", "10:30"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "iv_crush",
        "times": ["09:45"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "monday_gap_fill",
        "times": ["10:15", "10:30", "10:45", "11:00", "11:15", "11:30"],
        "weekdays": "mon",
    },
    {
        "rule_id": "tuesday_high_low",
        "times": ["09:30", "09:45", "10:00", "10:15", "10:30"],
        "weekdays": "tue",
    },
    {
        "rule_id": "wednesday_midweek",
        "times": ["14:00", "14:15", "14:30", "14:45", "15:00", "15:30", "15:45", "16:00"],
        "weekdays": "wed",
    },
    {
        "rule_id": "friday_gamma_squeeze",
        "times": ["14:30", "14:45", "15:00", "15:15", "15:30", "15:45", "16:00", "16:10", "16:20", "16:30", "16:40", "16:50"],
        "weekdays": "fri",
    },
]

# APScheduler: seconds to wait before treating a missed job as stale
MISFIRE_GRACE_SECONDS = 300

# Desktop UI background monitor (local app only — server uses SCHEDULED_CHECKS)
POLL_INTERVAL_SECONDS = 30