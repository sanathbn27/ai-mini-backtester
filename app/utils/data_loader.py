import pandas as pd
from typing import Dict, Union
import os
import datetime


MIN_DATE = datetime.date(2020, 1, 1)
MAX_DATE = datetime.date(2025, 1, 22)


class DataLoader:
    """
    Simple DataLoader that caches parquet DataFrames in memory.
    Exposes helper to get a row (Series) for a particular date.
    """

    def __init__(self, base_path: str = "data/generated_parquet"):
        self.base_path = base_path
        self._cache: Dict[str, pd.DataFrame] = {}

    def _path_for_field(self, field_name: str) -> str:
        return os.path.join(self.base_path, f"{field_name}.parquet")

    # To load single parquet file
    def _load_field(self, field_name: str) -> pd.DataFrame:
        """
        Load a parquet file for a data field and cache it.
        The returned DataFrame has index = DatetimeIndex and columns = security IDs (strings).
        """

        # check cache first
        if field_name in self._cache:
            return self._cache[field_name]

        path = self._path_for_field(field_name)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Dataset for field '{field_name}' not found at {path}"
            )

        df = pd.read_parquet(path)

        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        self._cache[field_name] = df
        return df

    def get_row_for_date(
        self, field_name: str, dt: Union[datetime.date, str, pd.Timestamp]
    ) -> pd.Series:
        """
        Return a Series for the given date (dt may be date, str, or Timestamp).
        If exact date not found, raise KeyError. (Alternative: implement ffill/backfill).
        """

        df = self._load_field(field_name)
        ts = pd.to_datetime(dt).date()

        # Validate date range
        if ts < MIN_DATE or ts > MAX_DATE:
            raise ValueError(
                f"Date {ts} is outside dataset range. "
                f"Please enter a date between {MIN_DATE} and {MAX_DATE}."
            )

        ts = pd.Timestamp(ts)

        # Use .loc for exact match, raise if missing
        try:
            row = df.loc[ts]
        except KeyError:
            # throw error
            raise KeyError(
                f"Date {ts.date()} not found in dataset for field '{field_name}'"
            )

        # Ensure it's a pandas Series
        if isinstance(row, pd.DataFrame):
            # If row returns DataFrame due to multiple identical indices, pick the first
            row = row.iloc[0]
        return row
