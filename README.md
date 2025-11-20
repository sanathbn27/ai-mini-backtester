# ai-mini-backtester
Mini Backtesting API using FastAPI, Python, Pandas, Paraquet, LLMs and Docker


## Features (Initial Setup)

- FastAPI project scaffold
- Modular architecture
- Separate endpoints:
  - `/api/backtest` (structured JSON)
  - `/api/backtest-prompt` (prompt-based, placeholder for now)
- Conda environment support
- Docker support

## How to set up

### Create conda env

```
conda env create -f environment.yml
conda activate bita_env
```