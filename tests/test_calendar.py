from app.utils.calendar import generate_quarter_dates

def test_basic_calendar_generation():
    dates = generate_quarter_dates(initial_date="2023-06-21")
    # Expected quarter ends
    assert dates == [
        # starting quarter end
        __import__("datetime").date(2023, 6, 30),
        __import__("datetime").date(2023, 9, 30),
        __import__("datetime").date(2023, 12, 31),
        __import__("datetime").date(2024, 3, 31),
        __import__("datetime").date(2024, 6, 30),   
        __import__("datetime").date(2024, 9, 30),
        __import__("datetime").date(2024, 12, 31),
    ]

def test_initial_date_on_quarter_end():
    dates = generate_quarter_dates(initial_date="2024-03-31")
    # Should include the initial date itself
    assert dates[0] == __import__("datetime").date(2024, 3, 31)

def test_initial_date_in_past():
    dates = generate_quarter_dates(initial_date="2022-01-10")
    # Should start from 2022-03-31
    assert dates[0] == __import__("datetime").date(2022, 3, 31)

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
