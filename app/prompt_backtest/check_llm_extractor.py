import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
import asyncio
from app.prompt_backtest.llm_extractor import extract_with_llm


async def main():
    result = await extract_with_llm(
        "Run a backtest starting from 2023-01-01 with top 10 by volume"
    )
    print(result)


asyncio.run(main())
