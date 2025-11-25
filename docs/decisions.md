# Architecture & Implementation Decisions  
**AI Mini Backtester – Design Document**

## 1. Overview

This document explains the architectural and implementation choices made while building the AI Mini Backtester project.
The focus is on readability, extensibility, correctness and demonstrating production-grade engineering practices.

## 2. Architectural Principles
### 2.1 Separation of Concerns

The application was divided into clear layers:

- standard/ → pure backtesting engine, deterministic logic

- prompt_backtest/ → natural-language handling (LLM + regex)

- models/ → Pydantic request/response schemas

- data_loader → loading data and working with dates

- tests → to verify everything working

main.py → FastAPI routing & initialization

This ensures independent development, testing and extension.

### 2.2 Extensible Pydantic Models (check)

The backtest engine was designed to support future growth:

Calendar rules are modeled using discriminated unions (rule_type)

Portfolio filters use extensible filters (filter_type)

Weighting schemes use their own base schema (weighting_type)

Adding new methods involves:

Creating new Pydantic subclass

Adding it to the Union

Implementing algorithm in service layer

This demonstrates production-level extensibility.

## 3. Data Loading Decisions
### 3.1 Pre-loading the dataset

The dataset is loaded once at application startup to avoid repeated expensive I/O.
This matches how real-world portfolio engines operate.

### 3.2 Using class attribute / app state (change)

Instead of a global variable, the dataset loader uses FastAPI’s app.state, which is thread-safe and scalable.

## 4. Backtest Logic Decisions
### 4.1 Vectorized Pandas operations

The engine uses:

- Groupby operations
- Numpy vectorized math
- Merging only necessary slices
- This avoids Python-level loops and ensures performance

### 4.2 Validation with Pydantic

**Date validation includes:**

- Future date rejection
- Out-of-range historical date rejection
- Flexible date parsing for prompt cases
- Pydantic ensures both correctness and clean API documentation.

## 5. Natural Language Understanding (NLU)
### 5.1 Primary LLM Parsing (Ollama + Llama3-8B)

**LLama3-8B is used because:**

- It runs locally
- Fast inference
- Very good at structured extraction
- Reliable JSON output with proper prompting

### 5.2 Retry Logic

The LLM call has retry logic to handle:

- transient network failure
- slow startup of Ollama server
- rare model warm-up issues
- This improves robustness without complicating the API layer.

### 5.3 Regex Fallback

A deterministic fallback layer exists to:

- support extremely simple prompts
- act as a safety net
- ensure predictable behavior when LLM fails

### 5.4 Important Behavior: LLM Dominates Regex

Well-known issue in hybrid NLP systems:

Modern LLMs interpret even loosely related text as valid input.

Because Llama3 is highly capable, it successfully extracts information even from vague prompts (e.g., “top 30 prices”) LLM still infers { "n": 30, "data_field": "prices" }.

Therefore, regex fallback rarely activates.

This is expected, documented and mirrors real production assistants.

When LLM returns a partial but valid response, default values are applied
```json
DEFAULTS = {
    "initial_date": "2020-01-01",
    "n": 10,
    "data_field": "market_capitalization",
    "filter_type": "TopN",
    "weighting_type": "Equal",
}
```

When LLM truly cannot interpret the prompt (e.g., “I am going for running, would you want to join”), the fallback activates and the system returns a meaningful error.

This is an intentional design decision.

## 6. Testing Strategy
### 6.1 Unit Tests

Tests cover:

- Calendar rule validation

- Filter validation

- Weighting model

- Backtest endpoint edge cases

- Model date validation

### 6.2 Prompt-based Testing 

LLM pipeline tested separately in isolation

Regex tested independently

Full pipeline test ensures end-to-end correctness

### 6.3 Test philosophy

Use pytest.raises for validation errors

Use httpx.AsyncClient for endpoint testing

Build tests that demonstrate robustness, not happy-path only

## 7. LLM Failure Handling
### 7.1 Why LLM sometimes fails first attempt

Ollama occasionally delays response while:

- loading model into memory
- performing warm-up
- cache refresh
- Windows background process delay
- Retry mechanism fixes this.

<!-- ### 7.2 Documented in README + decisions.md (change this info)

This avoids confusion during interview evaluation. -->

## 8. Docker (Not included yet)

The project is structured for containerization, including environment variable support for:

Docker support is included for running the API backend
- Ollama is not bundled inside Docker
- The container connects to host-running Ollama using OLLAMA_HOST
```bash
-e OLLAMA_HOST=http://host.docker.internal:11434
```
This allows the API running inside Docker to communicate with the LLM running on the host.
- Backtest API (structured endpoint) works fully inside Docker
- Prompt backtest works if host Ollama is running correctly
```powershell
ollama serve
```
and the model llama3:8b is available, /api/backtest-prompt works exactly the same inside Docker.

## 9. Trade-offs & Rejections

| Decision | Reason |
|---------|--------|
| Use local LLM, not OpenAI API | offline requirement, cost, deterministic output |
| Regex fallback kept simple | intended only as backup |
| Do not add complex strategies | out of scope; simplicity preferred |
| No database | dataset is read-only and small |

## 10. Conclusion

This solution demonstrates:

- clean architecture
- scalable model structure
- safe validation
- hybrid LLM + regex NLU
- thorough testing
- production-grade error handling
- extensibility for future features

Everything was implemented with clarity, maintainability and real-world engineering constraints in mind.