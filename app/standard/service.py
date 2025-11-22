import time
from typing import Dict
import numpy as np
from app.standard.models import BacktestRequest
from app.utils.calendar import generate_quarter_dates
from app.utils.data_loader import DataLoader
from pathlib import Path

# Data loader
BASE_DATA_PATH = Path("data") / "generated_parquet"
DATALOADER = DataLoader(str(BASE_DATA_PATH))

VALID_FIELDS = ["market_capitalization", "prices", "volume", "adtv_3_month"]


def run_backtest(request: BacktestRequest) -> Dict:
    """
    Core backtest engine:
    - generates calendar dates (quarterly)
    - for each date, loads the chosen data field and selects Top N securities
    - applies equal weighting
    - returns execution time and nested weights dict
    """

    start_time = time.perf_counter()

    # Calendar dates
    initial_date = request.calendar_rules.initial_date
    dates = generate_quarter_dates(initial_date)

    weights_result = {}

    if request.portfolio_creation.data_field not in VALID_FIELDS:
        raise ValueError(f"Invalid data_field: {request.portfolio_creation.data_field}")

    # Vectorized-ish per date: still iterate over review dates
    # but per-date selection uses pandas Series.nlargest which is optimized.
    for dt in dates:
        # Get the row (Series) for the desired data field
        try:
            series = DATALOADER.get_row_for_date(
                request.portfolio_creation.data_field, dt
            )
        except KeyError as e:
            raise KeyError(str(e))

        # Drop NaNs (if any)
        series = series.dropna()
        if series.empty:
            raise ValueError(
                f"No data available for date {dt} in field {request.portfolio_creation.data_field}"
            )

        n = request.portfolio_creation.n
        if n <= 0:
            # invalid n
            raise ValueError("n must be a positive integer")

        # Select top-n securities using Series.nlargest (fast)
        topn = series.nlargest(n)
        selected = topn.index.tolist()
        count = len(selected)
        if count == 0:
            raise ValueError(f"No securities selected for date {dt}")

        # Equal weights: assign 1/count to each security
        weight = 1.0 / float(count)
        # Build mapping as strings to floats (JSON serializable)
        weights_result[str(dt)] = {
            str(ind): float(np.round(weight, 5)) for ind in selected
        }

    execution_time = time.perf_counter() - start_time

    return {"execution_time_seconds": execution_time, "weights": weights_result}
