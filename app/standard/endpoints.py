from fastapi import APIRouter

router = APIRouter()

@router.post("/backtest")
def run_backtest():
    return {"message": "Standard backtest endpoint placeholder"}
