from fastapi import APIRouter

router = APIRouter()

@router.post("/backtest-prompt")
def run_backtest_prompt():
    return {"message": "Prompt endpoint placeholder"}
