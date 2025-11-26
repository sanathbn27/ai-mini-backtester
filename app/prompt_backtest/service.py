from typing import Dict, Any
from app.prompt_backtest.llm_extractor import extract_with_llm
from app.prompt_backtest.regex_fallback import extract_with_regex
from app.standard.models import (
    BacktestRequest,
    QuarterlyCalendar,
    TopNFilter,
    EqualWeighting,
)
from app.standard.service import run_backtest
from datetime import datetime
from pydantic import ValidationError

# Defaults values
DEFAULTS = {
    "initial_date": "2020-01-01",
    "n": 10,
    "data_field": "market_capitalization",
    "filter_type": "TopN",
    "weighting_type": "Equal",
}


# Dataset path default
DEFAULT_DATASET_PATH = "data/generated_parquet"


def parse_date_flexibly(date_str: str) -> datetime.date:
    """
    Try multiple formats for user/LLM input.
    """
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%y", "%m/%d/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")


def build_structured_from_parsed(parsed: Dict[str, Any]) -> BacktestRequest:
    """
    Given a partial parsed dict from LLM or regex, fill defaults and
    construct a BacktestRequest Pydantic model (used by /backtest).
    """
    # Fill defaults
    # Initial date
    raw_date = parsed.get("initial_date")
    if raw_date:
        initial_date = parse_date_flexibly(raw_date)
    else:
        initial_date = parse_date_flexibly(DEFAULTS["initial_date"])

    # Top N
    raw_n = parsed.get("n", DEFAULTS["n"])
    try:
        n = int(raw_n)
    except (TypeError, ValueError):
        n = DEFAULTS["n"]

    # Data field
    data_field = parsed.get("data_field", DEFAULTS["data_field"])

    # Build the Pydantic models
    calendar = QuarterlyCalendar(initial_date=initial_date)
    portfolio = TopNFilter(n=n, data_field=data_field)
    weighting = EqualWeighting()

    request = BacktestRequest(
        calendar_rules=calendar,
        portfolio_creation=portfolio,
        weighting=weighting,
    )

    return request


async def parse_prompt_to_request(prompt_text: str) -> Dict:
    """
    Try LLM extraction first. If LLM fails (None or invalid), fall back to regex.
    Returns a BacktestRequest ready to be passed to run_backtest().
    """
    # LLM
    parsed = await extract_with_llm(prompt_text)
    print("LLM parsed:", parsed)

    if isinstance(parsed, dict) and parsed:
        # Valid NON-empty dict → use LLM result
        try:
            return build_structured_from_parsed(parsed)
        except Exception as e:
            # LLM produced dict but invalid → fall through to regex
            print("LLM produced invalid dict, falling back to regex:", e)

    # Try regex fallback
    parsed_regex = extract_with_regex(prompt_text)
    print("Regex parsed:", parsed_regex)

    if isinstance(parsed_regex, dict) and parsed_regex:
        try:
            return build_structured_from_parsed(parsed_regex)

        except ValidationError as e:
            raise

        except Exception as e:
            print("Regex parse also failed:", e)

    # Fully invalid prompt
    raise ValueError("Invalid backtest prompt. Please enter a valid query.")


async def run_prompt_backtest(prompt_text: str) -> Dict:
    """
    High-level helper: parse the prompt, run the backtest engine and return result.
    """
    request = await parse_prompt_to_request(prompt_text)
    # We re-use the same run_backtest engine that /backtest uses
    print(f"Running backtest with request: {request}")
    result = run_backtest(request)
    return result
