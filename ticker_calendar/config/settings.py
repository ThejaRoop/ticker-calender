from datetime import date, timedelta

RECURRENCE_DAYS = 90
CALENDAR_YEARS = 3

TODAY = date.today()
CALENDAR_START = TODAY.replace(day=1)
CALENDAR_END = TODAY + timedelta(days=365 * CALENDAR_YEARS)
