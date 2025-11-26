# ai-mini-backtester
 
**Tech Stack:** Python 3.11, FastAPI, Pydantic, Pandas, NumPy, Ollama LLM  
**Tests:** Pytest  
**Deployment-Ready:** Conda or Docker


## Features 
This repository implements a **mini backtesting engine** and a **prompt-driven backtest interface** using:

- FastAPI project scaffold
- Modular architecture
- Separate endpoints:
  - `/api/backtest` (structured JSON)
  - `/api/backtest-prompt` (prompt-based)
- Conda environment support
- Docker support

The project follows a **modular, extensible architecture** suitable for adding:
* More calendar rules
* More portfolio filters
* More weighting schemes
* Additional model-driven NLU/LLM components

This document describes how to set up, run, test and understand the system.

## Project Structure

The application is structured into clearly separated modules for maintainability and extensibility.

```
app/
│── prompt_backtest/     # LLM interface + parser logic
│   ├── check_full_pipeline.py      # to check individual work flow
│   ├── check_llm_extractor.py
│   ├── check_regex_fallback.py
│   ├── endpoints.py
│   ├── prompt.py
│   ├── llm_extractor.py
│   ├── regex_fallback.py
│   ├── service.py
│── standard/            # Core deterministic backtest engine
│   ├── endpoints.py
│   ├── models.py
│   ├── service.py
│── Utils/
│   ├── calendar.py
│   ├── data_loader.py
│── main.py              # FastAPI application
│
data/
│── generated_parquet/   # Generated synthetic dataset
│── data_generation.py     # script to build dataset
│
docs/
│── decisions.md   
│── docker_run.md    
│── LLm_setup.md
│
tests/
│── test_backtest_endpoint.py
│── test_backtest_prompt.py
│── ...
│
Dockerfile
environment.yml
README.md
requirements.txt
```
# 🔧 Installation

## 1. Clone the repository

```bash
git clone https://github.com/sanathbn27/ai-mini-backtester.git
cd ai-mini-backtester
```

## 2. Create Virtual Env

**using env.yml**

```bash
conda env create -f environment.yml
conda activate bita_env
```
**OR**

**using conda and pip**

Install dependencies using `pip`:

```bash
conda create -n bita_env python=3.11
conda activate bita_env
pip install -r requirements.txt
```
---
# Local and Docker Options

This project supports **two ways** to run:

---

## OPTION A — Local Setup
**Best for development**   
**Full LLM functionality**  
**Works on any Python 3.11 environment**
**Detail information of the project in this README.md file**


## OPTION B — Docker Setup  
**Backtest API works fully; LLM prompt API may fail sometimes and fallback to regex** 

Follow detailed instructions to run the project using docker:  
**docs/docker_run.md**

---

## OPTION A - Local Setup

## 3. How to set up

### Generating Data (Parquet files)

Before running the API, you must generate the synthetic time-series datasets used for backtesting:
Go to the path where you cloned the project and run in the terminal:
```bash
python data/data_generation.py
```
This command produces the following files in the data/generated_parquet/ directory:

- prices.parquet
- volume.parquet
- market_capitalization.parquet
- adtv_3_month.parquet

### Running the API (Local Development)

Start the FastAPI server with auto-reload for local development:
Go to the ai-mini-backtester folder path then
```bash
uvicorn app.main:app --reload
```

The interactive Swagger documentation is available at: http://127.0.0.1:8000/docs

## 4. Standard Backtest Endpoint

POST /api/backtest
Runs a deterministic backtest using a structured JSON input defined by the underlying Pydantic models.
Example Request:
```json
{
  "calendar_rules": { 
    "rule_type": "Quarterly", 
    "initial_date": "2023-01-01" 
  },
  "portfolio_creation": { 
    "filter_type": "TopN", 
    "n": 10, 
    "data_field": "volume" 
  },
  "weighting": { 
    "weighting_type": "Equal" 
  }
}
```

Example Response:
```json
{
  "execution_time_seconds": 0.013,
  "weights": {
    "2023-03-31": { "12": 0.1, "55": 0.1, "...": "..." },
    "2023-06-30": { "...": "..." }
  }
}
```

## 5. Prompt Based Backtest Endpoint

POST /api/backtest-prompt
This endpoint runs the same backtest engine but adds a Natural Language Understanding (NLU)/ LLM layer:

- Accepts natural language
- Uses LLM (Ollama) to extract backtest parameters
- Falls back to regex if LLM fails (check this)
- Applies defaults if fields are missing
- Validated through Pydantic
- Bactest executed

Follow these steps to install, run, test and troubleshoot the LLM Ollama model before testing.

**docs/LLM_setup.md**

Example Request:
```json
{ 
  "prompt": "Run a backtest starting from 2023-01-01 with top 50 by volume" 
}
```

Example Parsed Result (Internal):
The NLU/LLM layer transforms the prompt into the required parameters:

```json
{
  "initial_date": "2023-01-01",
  "n": 50,
  "data_field": "volume"
}
```

Notes:
The LLM may return incomplete output based on the user prompt; safe defaults are applied.

If the LLM parsing fails validation, a controlled error is returned.

### Testing LLm, Regex and Full Pipeline (Standalone Scripts)

To make debugging easier and to avoid testing inside the API manually,
the project includes three dedicated testing scripts:

- Test LLM Extractor Only

Runs the LLM directly and prints the extracted JSON dictionary.

```bash 
python app/prompt_backtest/check_llm_extractor.py
```

- Test Regex Fallback Only

Runs the regex-based parameter extractor without involving LLM.

```bash
python app/prompt_backtest/check_regex_fallback.py
```

- Test Full Backtest Prompt Pipeline

Runs the entire parsing pipeline used inside the /api/backtest-prompt endpoint.

```bash
python app/prompt_backtest/check_full_pipeline.py
```


## 6. Running Tests

The repository includes a comprehensive test suite using pytest.
```bash
pytest -q
```

The tests cover:

- Calendar generation
- Data loader functionality
- Pydantic model validation
- Standard backtest endpoint logic
- Prompt-based endpoint flow

## 7. Additional Files

| File | Description |
|------|-------------|
| **llm_setup.md** | Full instructions for installing & configuring Ollama |
| **docker_run.md** | Complete Docker guide + known issues + fallback behavior |
| **decisions.md** | Architecture decisions, work flow, trade-offs |

# Final Notes

- Code is modular, production-style and extensible  
- Backtest engine is fully deterministic  
- Prompt parser is resilient: LLM → patch → regex → defaults  
- Docker available for easy deployment  
- LLM runs only on host machine (documented)  

This repo demonstrates strong engineering fundamentals:  
clean structure, typed models, validation, extensibility and clear documentation.