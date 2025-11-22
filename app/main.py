from fastapi import FastAPI
from app.standard.endpoints import router as standard_router
from app.prompt_backtest.endpoints import router as prompt_router

app = FastAPI(title="AI Mini Backtester")

# Standard backtest endpoint (structured input)
app.include_router(standard_router, prefix="/api")

# Prompt-based backtest endpoint 
app.include_router(prompt_router, prefix="/api")
