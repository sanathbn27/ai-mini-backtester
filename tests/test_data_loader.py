import os
import pandas as pd
import numpy as np
from app.utils.data_loader import DataLoader

TEST_PATH = "data/generated_parquet"

def test_load_field_success():
    loader = DataLoader(TEST_PATH)
    df = loader._load_field("market_capitalization")  # should exist
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 1000  # securities
    assert len(df.index) > 0        # dates

def test_load_field_missing():
    loader = DataLoader(TEST_PATH)
    try:
        loader._load_field("does_not_exist")
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True

def test_get_row_for_date_success():
    loader = DataLoader(TEST_PATH)
    df = loader._load_field("prices")
    sample_date = df.index[0]  # first available date
    row = loader.get_row_for_date("prices", sample_date)
    assert isinstance(row, pd.Series)
    assert len(row) == 1000  # securities

def test_get_row_missing_date():
    loader = DataLoader(TEST_PATH)
    try:
        loader.get_row_for_date("prices", "1999-01-01")
        assert False, "Expected ValueError for out-of-range date"
    except ValueError:
        assert True

def test_cache_usage():
    loader = DataLoader(TEST_PATH)
    df1 = loader._load_field("volume")
    df2 = loader._load_field("volume")
    assert df1 is df2  # same object due to cache

def test_date_out_of_range():
    loader = DataLoader(TEST_PATH)
    try:
        loader.get_row_for_date("prices", "2019-12-31")
        assert False, "Expected ValueError for date out of range"
    except ValueError as e:
        assert "outside dataset range" in str(e)

