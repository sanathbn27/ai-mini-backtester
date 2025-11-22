import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, timedelta

client = TestClient(app)


# Helper: build a valid request payload
def valid_payload():
    return {
        "calendar_rules": {"initial_date": "2023-01-01"},
        "portfolio_creation": {"n": 5, "data_field": "volume"},
        "weighting": {},
    }


# Happy Path Test
def test_backtest_success():
    payload = valid_payload()
    response = client.post("/api/backtest", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "execution_time_seconds" in data
    assert "weights" in data
    assert isinstance(data["weights"], dict)


# Validation Errors
def test_backtest_invalid_n_zero():
    payload = valid_payload()
    payload["portfolio_creation"]["n"] = 0

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 400
    assert "n must be a positive integer" in resp.json()["detail"]


def test_backtest_missing_calendar_rules():
    payload = valid_payload()
    del payload["calendar_rules"]

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 422  # Pydantic validation error


def test_backtest_missing_data_field():
    payload = valid_payload()
    del payload["portfolio_creation"]["data_field"]

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 422


def test_backtest_invalid_date_format():
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = "not-a-date"

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 422


def test_backtest_future_date_rejected():
    future_date = (date.today() + timedelta(days=5)).isoformat()
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = future_date

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 422  # Pydantic validation
    assert "cannot be in the future" in str(resp.json())


# Dataset Errors
def test_backtest_invalid_data_field():
    payload = valid_payload()
    payload["portfolio_creation"]["data_field"] = "UNKNOWN_FIELD"

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 400
    assert "Invalid data_field" in resp.json()["detail"]


def test_backtest_date_not_in_dataset():
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = "1990-01-01"  # older than MIN_DATE

    resp = client.post("/api/backtest", json=payload)

    assert resp.status_code == 400
    assert "outside dataset range" in resp.json()["detail"]


# 4. Boundary Tests
def test_backtest_initial_date_min_allowed():
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = "2020-01-01"

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 200


def test_backtest_initial_date_max_allowed():
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = "2025-01-22"

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 200


def test_backtest_initial_date_above_max():
    payload = valid_payload()
    payload["calendar_rules"]["initial_date"] = "2025-12-31"

    resp = client.post("/api/backtest", json=payload)
    assert resp.status_code == 422
    assert "cannot be in the future" in resp.text
