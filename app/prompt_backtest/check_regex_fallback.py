import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
from app.prompt_backtest.regex_fallback import extract_with_regex

tests = [
    "Run a backtest starting from 2020-01-01",
    "top 50 by volume",
    "market_capitalization top 10",
    "start 2023-05-15 volume",
]

for t in tests:
    print("PROMPT:", t)
    print("PARSED:", extract_with_regex(t))
    print("------")
