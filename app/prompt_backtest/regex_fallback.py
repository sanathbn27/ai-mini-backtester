# app/nlu/regex_fallback.py
import re
from typing import Dict, Optional

# mapping of synonyms to canonical data_field names
DATA_FIELD_ALIASES = {
    "market_cap": "market_capitalization",
    "marketcap": "market_capitalization",
    "market capitalization": "market_capitalization",
    "market_capitalization": "market_capitalization",
    "price": "prices",
    "prices": "prices",
    "volume": "volume",
    "vol": "volume",
    "adtv": "adtv_3_month",
    "adtv_3_month": "adtv_3_month",
    "average daily traded volume": "adtv_3_month",
}

DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
TOPN_RE = re.compile(r"\btop\s+(\d{1,4})\b", re.IGNORECASE)
NUM_RE = re.compile(r"\b(\d{1,4})\s+(?:securities|stocks|tickers)\b", re.IGNORECASE)


def extract_with_regex(prompt: str) -> Dict:
    """
    Extracts possible fields from prompt using heuristics:
    - initial_date: first YYYY-MM-DD found
    - n: first occurrence of "top N" or "<N> securities"
    - data_field: first known keyword / alias found
    Returns a dict that may contain any subset of keys.
    """
    out = {}

    # date
    m = DATE_RE.search(prompt)
    if m:
        out["initial_date"] = m.group(1)

    # top N
    m = TOPN_RE.search(prompt)
    if m:
        out["n"] = int(m.group(1))
    else:
        # fallback to "<N> securities"
        m2 = NUM_RE.search(prompt)
        if m2:
            out["n"] = int(m2.group(1))

    # detect data_field by scanning tokens for known aliases
    # simple token scanning
    lowered = prompt.lower()
    for alias, canonical in DATA_FIELD_ALIASES.items():
        if alias in lowered:
            out["data_field"] = canonical
            break

    return out
