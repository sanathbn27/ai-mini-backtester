from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict
from datetime import date
import os


# Calendar models
class QuarterlyCalendar(BaseModel):
    rule_type: Literal["Quarterly"] = "Quarterly"
    initial_date: date

    @field_validator("initial_date")
    def date_cannot_be_in_future(cls, date):
        import datetime

        today = datetime.date.today()
        if date > today:
            raise ValueError(
                f"initial_date {date} cannot be in the future (today is {today})."
            )
        return date


# Portfolio creation models
class TopNFilter(BaseModel):
    filter_type: Literal["TopN"] = "TopN"
    n: int
    data_field: str


# Weighting models
class EqualWeighting(BaseModel):
    weighting_type: Literal["Equal"] = "Equal"


# Full backtest request (modular)
class BacktestRequest(BaseModel):
    calendar_rules: QuarterlyCalendar
    portfolio_creation: TopNFilter
    weighting: EqualWeighting
    # # dataset_identifier: optional override (path under data/parquet)
    # dataset_path: str = os.path.join("data", "generated_parquet")


# Response model (informal - not strictly required by FastAPI for serialization)
class BacktestResponse(BaseModel):
    execution_time_seconds: float
    weights: Dict[str, Dict[str, float]]
