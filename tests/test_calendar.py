from app.utils.calendar import generate_quarter_dates
import datetime

def test_basic_calendar_generation():
    dates = generate_quarter_dates(initial_date="2023-06-21")
    # Expected quarter ends
    assert dates == [
        # starting quarter end
        datetime.date(2023, 6, 30),
        datetime.date(2023, 9, 30),
        datetime.date(2023, 12, 31),
        datetime.date(2024, 3, 31),
        datetime.date(2024, 6, 30),   
        datetime.date(2024, 9, 30),
        datetime.date(2024, 12, 31),
    ]

def test_initial_date_on_quarter_end():
    dates = generate_quarter_dates(initial_date="2024-03-31")
    # Should include the initial date itself
    assert dates[0] == datetime.date(2024, 3, 31)

def test_initial_date_in_past():
    dates = generate_quarter_dates(initial_date="2022-01-10")
    # Should start from 2022-03-31
    assert dates[0] == datetime.date(2022, 3, 31)

def test_edge_case_end_date():
    # Starting at last allowed date
    # 2025-01-22 falls inside Q1, quarter end = 2025-03-31 (beyond end)
    dates = generate_quarter_dates(initial_date="2025-01-22")
    # Should generate empty because Q-end is > DEFAULT_END_DATE
    assert dates == []

def test_large_range():
    # Just confirming no errors for wide spans
    dates = generate_quarter_dates(initial_date="2020-01-01")
    assert len(dates) > 10  


def test_custom_end_date_limits_range():
    # Custom end date before default
    dates = generate_quarter_dates(
        initial_date="2023-01-01",
        end_date="2023-06-30"
    )
    assert dates == [
        datetime.date(2023, 3, 31),
        datetime.date(2023, 6, 30),
    ]

def test_end_date_before_initial_date():
    # Custom end date before initial date
    dates = generate_quarter_dates(
        initial_date="2023-06-01",
        end_date="2023-03-31"
    )
    assert dates == []

