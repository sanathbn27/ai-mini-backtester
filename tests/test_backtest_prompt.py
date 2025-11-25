import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


# Valid prompt -> valid response
@patch("app.prompt_backtest.llm_extractor.extract_with_llm")
def test_backtest_prompt_valid(mock_llm):
    mock_llm.return_value = {
        "initial_date": "2023-01-01",
        "n": 5,
        "data_field": "volume",
    }

    payload = {"prompt": "Run a backtest starting from 2023-01-01 with top 5 by volume"}

    resp = client.post("/api/backtest-prompt", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "execution_time_seconds" in data
    assert "weights" in data
    assert isinstance(data["weights"], dict)


# Missing fields -> defaults applied
@patch("app.prompt_backtest.llm_extractor.extract_with_llm")
def test_backtest_prompt_defaults(mock_llm):
    mock_llm.return_value = {
        "initial_date": "2022-01-01"
        # missing n, missing data_field
    }

    payload = {"prompt": "Start backtest from 2022-01-01"}

    resp = client.post("/api/backtest-prompt", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # We cannot check exact weights, but API shape must hold
    assert "execution_time_seconds" in data
    assert "weights" in data


# Invalid date (future) -> returns 422
@patch("app.prompt_backtest.llm_extractor.extract_with_llm")
def test_backtest_prompt_future_date(mock_llm):
    mock_llm.return_value = {
        "initial_date": "2099-01-01",  # invalid
        "n": 5,
        "data_field": "prices",
    }

    payload = {"prompt": "Run test in 2099-01-01 for price"}

    resp = client.post("/api/backtest-prompt", json=payload)
    assert resp.status_code == 422
    assert "cannot be in the future" in resp.text


# Nonsense prompt -> LLM returns None -> 400 error
@patch("app.prompt_backtest.llm_extractor.extract_with_llm")
def test_backtest_prompt_llm_none(mock_llm):
    mock_llm.return_value = None

    payload = {"prompt": "gibberish gibberish wowowow"}

    resp = client.post("/api/backtest-prompt", json=payload)
    assert resp.status_code == 422
    assert "Invalid backtest prompt" in resp.text


@patch("app.prompt_backtest.llm_extractor.extract_with_llm")
def test_backtest_prompt_llm_error(mock_llm):
    mock_llm.side_effect = RuntimeError("Model error")

    payload = {"prompt": "Start on 2023-01-01"}

    resp = client.post("/api/backtest-prompt", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # We cannot check exact weights, but API shape must hold
    assert "execution_time_seconds" in data
    assert "weights" in data


# 7. Missing prompt in request -> 422 (validation)
def test_backtest_prompt_missing_field():
    resp = client.post("/api/backtest-prompt", json={})
    assert resp.status_code == 422
