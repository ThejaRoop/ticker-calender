from unittest.mock import patch

from ticker_calendar.services.notification_service import format_alert_message, send_ntfy
from ticker_calendar.rules.evaluator import AlertCandidate
from datetime import date


def test_format_alert_message():
    candidate = AlertCandidate(
        rule_id="earnings_today",
        rule_name="Earnings Today",
        ticker="MSFT",
        message="There is a chance to buy call for MSFT",
        alert_date=date(2026, 7, 8),
    )
    text = format_alert_message(candidate)
    assert "MSFT" in text
    assert "Earnings Today" in text


@patch("ticker_calendar.services.notification_service.requests.post")
def test_send_ntfy_success(mock_post):
    mock_post.return_value.status_code = 200
    assert send_ntfy("test message") is True
    mock_post.assert_called_once()
