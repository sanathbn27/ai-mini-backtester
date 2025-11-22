import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from app.standard.models import QuarterlyCalendar, TopNFilter, EqualWeighting, BacktestRequest


def test_quarterly_calendar_valid():
    c = QuarterlyCalendar(initial_date=date(2023, 1, 1))
    assert c.initial_date == date(2023, 1, 1)
    assert c.rule_type == "Quarterly"


def test_quarterly_calendar_future_date_rejected():
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationError):
        QuarterlyCalendar(initial_date=future_date)


def test_quarterly_calendar_invalid_date_format():
    with pytest.raises(ValidationError):
        QuarterlyCalendar(initial_date="not-a-date")


def test_quarterly_calendar_rule_type_cannot_change():
    with pytest.raises(ValidationError):
        QuarterlyCalendar(rule_type="Monthly", initial_date=date(2023, 1, 1))


#for top-n filter tests
def test_topnfilter_valid():
    f = TopNFilter(n=10, data_field="volume")
    assert f.n == 10
    assert f.data_field == "volume"
    assert f.filter_type == "TopN"


def test_topnfilter_negative_n_allowed_by_model():
    # Pydantic DOES allow negative int. Endpoint later blocks it.
    f = TopNFilter(n=-5, data_field="prices")
    assert f.n == -5


def test_topnfilter_missing_data_field():
    with pytest.raises(ValidationError):
        TopNFilter(n=10)


def test_topnfilter_invalid_filter_type():
    with pytest.raises(ValidationError):
        TopNFilter(filter_type="BottomN", n=10, data_field="prices")


# equal weighting tests
def test_equal_weighting_valid():
    w = EqualWeighting()
    assert w.weighting_type == "Equal"


def test_equal_weighting_invalid_type():
    with pytest.raises(ValidationError):
        EqualWeighting(weighting_type="Custom")

# backtest request tests
def test_backtest_request_valid_payload():
    payload = {
        "calendar_rules": {"initial_date": "2023-01-01"},
        "portfolio_creation": {"n": 5, "data_field": "volume"},
        "weighting": {}
    }

    req = BacktestRequest(**payload)
    assert req.calendar_rules.initial_date == date(2023, 1, 1)
    assert req.portfolio_creation.n == 5
    assert req.weighting.weighting_type == "Equal"


def test_backtest_request_missing_calendar_rules():
    payload = {
        "portfolio_creation": {"n": 5, "data_field": "prices"},
        "weighting": {}
    }

    with pytest.raises(ValidationError):
        BacktestRequest(**payload)


def test_backtest_request_missing_weighting():
    payload = {
        "calendar_rules": {"initial_date": "2023-01-01"},
        "portfolio_creation": {"n": 10, "data_field": "volume"}
    }

    with pytest.raises(ValidationError):
        BacktestRequest(**payload)


def test_backtest_request_invalid_portfolio_creation_type():
    payload = {
        "calendar_rules": {"initial_date": "2023-01-01"},
        "portfolio_creation": {"wrong": "value"},
        "weighting": {}
    }

    with pytest.raises(ValidationError):
        BacktestRequest(**payload)
