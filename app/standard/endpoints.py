from fastapi import APIRouter, HTTPException
from app.standard.models import BacktestRequest
from app.standard.service import run_backtest

router = APIRouter()


@router.post("/backtest")
def backtest_endpoint(request: BacktestRequest):
    """
    Standard backtest endpoint.
    Receives a structured JSON payload defined by BacktestRequest and returns engine output.
    """
    # Basic validation: ensure n is reasonable
    if request.portfolio_creation.n <= 0:
        raise HTTPException(status_code=400, detail="n must be a positive integer")

    try:
        result = run_backtest(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

    return result
