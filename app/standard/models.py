from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Dict
from datetime import date

# Calendar models
class QuarterlyCalendar(BaseModel):
    rule_type: Literal["Quarterly"] = "Quarterly"
    initial_date: date

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
    # dataset_identifier: optional override (path under data/parquet)
    dataset_path: str = "data\generated_parquet"

# Response model (informal - not strictly required by FastAPI for serialization)
class BacktestResponse(BaseModel):
    execution_time_seconds: float
    weights: Dict[str, Dict[str, float]]
