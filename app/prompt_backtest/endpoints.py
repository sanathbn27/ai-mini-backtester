from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.prompt_backtest.service import run_prompt_backtest

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/backtest-prompt")
async def backtest_prompt_endpoint(payload: PromptRequest) -> Dict[str, Any]:
    """
    Accepts {"prompt": "..."}.
    Tries to parse prompt (LLM -> regex fallback), runs backtest and returns SAME output
    shape as /backtest: { "execution_time_seconds": .., "weights": {...} }
    """
    prompt_text = payload.prompt
    if not prompt_text or not prompt_text.strip():
        raise HTTPException(status_code=400, detail="Prompt must be a non-empty string")

    try:
        result = await run_prompt_backtest(prompt_text)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run prompt backtest: {e}"
        )

    return result
