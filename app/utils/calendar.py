from datetime import date
import pandas as pd
from typing import List

DEFAULT_END_DATE = pd.Timestamp("2025-01-22").date()


def quarter_end_for_date(d: pd.Timestamp) -> pd.Timestamp:
    """Return the quarter-end timestamp for the month of the given timestamp."""

    # pd.Timestamp is convenient for quarter arithmetic
    quarter = (d.month - 1) // 3 + 1

    # Quarter end month is quarter*3
    q_end_month = quarter * 3

    # Last day of q_end_month:
    last_date = pd.Timestamp(
        year=d.year, month=q_end_month, day=1
    ) + pd.offsets.MonthEnd(0)
    return last_date


def generate_quarter_dates(
    initial_date: date, end_date: date = DEFAULT_END_DATE
) -> List[date]:
    """
    Generate quarter-end dates starting from the quarter containing initial_date
    up to and including end_date (inclusive).
    """
    if isinstance(initial_date, date):
        cur = pd.Timestamp(initial_date)
    else:
        cur = pd.to_datetime(initial_date)
    end = pd.Timestamp(end_date)

    # Start from the quarter-end of the initial date
    cur_q_end = quarter_end_for_date(cur)

    dates = []
    while cur_q_end <= end:
        dates.append(cur_q_end.date())
        # move forward one quarter
        cur_q_end = cur_q_end + pd.DateOffset(months=3)

        # adjust to quarter end (in case of month lengths)
        cur_q_end = quarter_end_for_date(cur_q_end)

    return dates
