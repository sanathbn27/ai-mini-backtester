# Docker Deployment Guide  

This guide explains how to run the application in Docker.

**Important note about Ollama + Docker on Windows**  
Ollama requires **direct GPU access** and **system-level permissions**.  
Docker Desktop on Windows **cannot expose NVIDIA GPU** to containers reliably.

Therefore:

> **Ollama cannot run inside the Docker container on Windows.**  
> Instead, the LLM must run on the **host machine** and the Docker container will call it externally.

LLM install instructions:  

Follow these steps to install, run, test and troubleshoot the LLM Ollama model.

Go to: **app/docs/LLM_setup.md**

---

# 1. Pre-requisites

Before building Docker:

### Install Ollama on host  
### Pull llama3:8b  
### Ensure LLM API works  
### Generate dataset locally  

Run:

```bash
python data/generate_data.py
```

This creates:

```
/data/generated_parquet/
```

The Docker container expects this folder to exist.

---

# 2. Build Docker image

In project root:

```bash
docker build -t backtester .
```

---

# 3. Run container (connecting to host’s Ollama)

Windows Docker uses:

```
host.docker.internal
```

Run container:

```bash
docker run -p 8000:8000 -e OLLAMA_HOST=http://host.docker.internal:11434 backtester
```

You should see:

```
Uvicorn running on http://0.0.0.0:8000
```

Access the API at:

http://127.0.0.1:8000/docs

- Note: If there is a problem running the ollama model, just run the below command without ollama model
still the `api/backtest` and `api/backtest-prompt` both will work, however the parsing of the prompt 
will happen with the regex 

```bash
docker run -p 8000:8000 -e backtester
```

## Standard Backtest Endpoint

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

## Prompt Based Backtest Endpoint

POST /api/backtest-prompt

This endpoint runs the same backtest engine but adds a Natural Language Understanding (NLU)/ LLM layer:


Example Request:
```json
{ 
  "prompt": "Run a backtest starting from 2023-01-01 with top 50 by volume" 
}
```

Example Parsed Result (Internal):
The NLU layer transforms the prompt into the required parameters:

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

---

# 4. Expected behavior in Docker

### Works perfectly
- Backtest endpoint (`/api/backtest`)
- Data access
- Pydantic validations
- All deterministic logic
- Regex fallback for simple prompts

### Limited (by design)
- Backtest-prompt endpoint (`/api/backtest-prompt`)
- LLM parsing (`extract_with_llm`)
- May fail sometimes due to networking restrictions in Windows Docker  
- When LLM fails → **automatic regex fallback**  
  

---

# 5. Validating endpoints

- Test deterministic endpoint:

In Git Bash:
```bash
curl -X POST "http://127.0.0.1:8000/api/backtest-prompt" -H "Content-Type: application/json" -d "{\"prompt\": \"Run a backtest starting from 2023-01-01 with top 10 by volume\"}"
```

In Powershell:
```bash
Invoke-WebRequest -Method POST http://127.0.0.1:11434/api/generate -Headers @{ "Content-Type" = "application/json" } -Body '{ "model": "llama3:8b", "prompt": "Run a backtest starting from 2023-01-01 with top 50 by volume", "stream": false }'
```

- Test prompt endpoint:

In Git Bash:
```bash
curl -X POST http://127.0.0.1:8000/api/backtest-prompt -H "Content-Type: application/json" -d '{"prompt":"top 10 volume"}'
```


If LLM cannot be reached, output will still be valid, regex takes over.

---

# 6. Summary

| Feature | Local | Docker |
|--------|--------|--------|
| Backtest Engine | ✅ | ✅ |
| Pydantic Validation | ✅ | ✅ |
| LLM Parsing | ✅ | ⚠ may fail |
| Regex Fallback | ✅ | ✅ |
| Runs Ollama Internally | ✅ | ❌ (not possible) |

---

# 7. Finished
Your Docker environment is ready.

You can now open Swagger API docs in your browser at:

    http://127.0.0.1:8000/docs

From there, you can run and verify both endpoints:
1. **/api/backtest** — structured JSON backtest  
2. **/api/backtest-prompt** — natural-language prompt backtest (LLM or regex)
 
## Output will be structured json 

- An execution_time_seconds field indicating how long the backtest took for the mentioned **data_field**.

- A weights dictionary showing equal-weighted portfolio allocations for each quarterly dates starting from the mentioned **date**.

- For each quarter (e.g., "2020-03-31", "2020-06-30"), the system assigns **1/N** equal weights to the **Top-N** selected securities.

- These weights correspond to the securities chosen by the strategy using the provided input parameters (structured JSON) or extracted parameters (LLM/regex).

