import asyncio
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
from app.prompt_backtest.service import parse_prompt_to_request


async def main():
    tests = [
        "Run a backtest starting from 2024-01-01 with top 50 by prices",
        "top 30 prices",
        "i am going for running, are you interested?",
    ]

    for t in tests:
        print("PROMPT:", t)
        try:
            req = await parse_prompt_to_request(t)
            print(" STRUCTURED:", req)
        except Exception as e:
            print(" ERROR:", e)

        print("------")


asyncio.run(main())
