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

RULE_POST_EARNINGS_MOMENTUM = {
    "id": "post_earnings_momentum",
    "name": "Post-Earnings Momentum Window (Day +1)",
    "requires_down": False,
}

RULE_MIDWEEK_EARNINGS_SETUP = {
    "id": "midweek_earnings_setup",
    "name": "Mid-Week Earnings Lookahead (Wednesday Setup)",
    "requires_down": False,
}

RULE_POPULAR_FRIDAY = {
    "id": "popular_friday",
    "name": "Popular Stocks Friday Watch",
    "requires_down": False,
}

RULE_MONTHLY_OPEX_FRIDAY = {
    "id": "monthly_opex_friday",
    "name": "Monthly Options Expiration (OPEX) Friday Watch",
    "requires_down": False,
}

RULE_QUARTER_END_REBALANCE = {
    "id": "quarter_end_rebalance",
    "name": "Month-End Institutional Flow Setup",
    "requires_down": False,
}

RULES_BY_ID = {
    RULE_EARNINGS_TODAY["id"]: RULE_EARNINGS_TODAY,
    RULE_EARNINGS_NEXT_WEEK["id"]: RULE_EARNINGS_NEXT_WEEK,
    RULE_EARNINGS_TOMORROW["id"]: RULE_EARNINGS_TOMORROW,
    RULE_EARNINGS_DAY_MORNING_MATRIX["id"]: RULE_EARNINGS_DAY_MORNING_MATRIX,
    RULE_POST_EARNINGS_MOMENTUM["id"]: RULE_POST_EARNINGS_MOMENTUM,
    RULE_MIDWEEK_EARNINGS_SETUP["id"]: RULE_MIDWEEK_EARNINGS_SETUP,
    RULE_POPULAR_FRIDAY["id"]: RULE_POPULAR_FRIDAY,
    RULE_MONTHLY_OPEX_FRIDAY["id"]: RULE_MONTHLY_OPEX_FRIDAY,
    RULE_QUARTER_END_REBALANCE["id"]: RULE_QUARTER_END_REBALANCE,
}

ALERT_MESSAGE = "There is a chance to buy call for {ticker}"
ALERT_MESSAGE_NEXT_WEEK = "There is a chance to buy call for {ticker} (earnings next week)"
ALERT_MESSAGE_TOMORROW = "There is a chance to buy call for {ticker} (earnings tomorrow)"
ALERT_MESSAGE_EARNINGS_MATRIX = "Earnings buy window open for {ticker}"
ALERT_MESSAGE_POST_EARNINGS_MOMENTUM = "Post-earnings volatility window active for {ticker}"
ALERT_MESSAGE_MIDWEEK_EARNINGS_SETUP = "Mid-week pre-earnings setup for {ticker} (reporting soon)"
ALERT_MESSAGE_MONTHLY_OPEX_FRIDAY = "Monthly OPEX volatility window open for {ticker}"
ALERT_MESSAGE_QUARTER_END_REBALANCE = "Month-end rebalancing flow window active for {ticker}"

# Curated watchlist for popular_friday rule
POPULAR_FRIDAY_WATCHLIST = ["MSFT", "GOOGL", "NVDA", "SPY"]

# Core high-liquidity tickers for OPEX rule
OPEX_CORE_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]

# Index proxies and major large-cap for quarter-end rule
QUARTER_END_TICKERS = ["SPY", "MSFT", "NVDA"]

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
        "rule_id": "post_earnings_momentum",
        "times": ["09:45", "10:00", "10:15", "10:30"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
    {
        "rule_id": "midweek_earnings_setup",
        "times": ["13:00", "13:15", "13:30", "13:45", "14:00"],
        "weekdays": "wed",
    },
    {
        "rule_id": "popular_friday",
        "times": ["10:00", "10:15", "10:30", "10:45"],
        "weekdays": "fri",
    },
    {
        "rule_id": "monthly_opex_friday",
        "times": ["10:30", "10:45", "11:00", "11:15", "11:30"],
        "weekdays": "fri",
    },
    {
        "rule_id": "quarter_end_rebalance",
        "times": ["15:00", "15:15", "15:30", "15:45"],
        "weekdays": "mon,tue,wed,thu,fri",
    },
]

# APScheduler: seconds to wait before treating a missed job as stale
MISFIRE_GRACE_SECONDS = 300

# Desktop UI background monitor (local app only — server uses SCHEDULED_CHECKS)
POLL_INTERVAL_SECONDS = 30