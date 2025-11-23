import json
from typing import Optional, Dict, Any
import httpx
from app.prompt_backtest.prompt import LLM_SYSTEM_PROMPT
import os
import asyncio

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_API = f"{OLLAMA_HOST}/api/generate"

# OLLAMA_API = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"


async def run_ollama_api(prompt_text: str, timeout: int = 15) -> str:
    """
    Call Ollama using the HTTP API instead of subprocess.
    Returns raw text output from the model.
    """

    combined_prompt = f"{LLM_SYSTEM_PROMPT}\n\nUser Prompt:\n{prompt_text}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            OLLAMA_API,
            json={
                "model": OLLAMA_MODEL,
                "prompt": combined_prompt,
                "stream": False,
            },
        )
        print("Ollama response status:", resp.status_code)
        # print("Ollama response text:", resp.text)
        resp.raise_for_status()
        data = resp.json()

    # The generated text is in data["response"]
    return data.get("response", "") or ""


async def extract_with_llm(
    prompt_text: str, retries: int = 2
) -> Optional[Dict[str, Any]]:
    """
    Calls Ollama API and extracts JSON dict from returned text.
    Returns None if JSON cannot be parsed.
    """

    for attempt in range(retries + 1):
        try:
            raw = await run_ollama_api(prompt_text)
            break  # success → exit retry loop
        except Exception as e:
            print(f"LLM CALL FAILED (attempt {attempt+1}): {e}")

            if attempt == retries:
                # all retries failed → return None
                return None

            # small wait before retrying
            await asyncio.sleep(0.4)

    if not raw:
        return None

    # Find JSON inside the raw response
    raw = raw.strip()
    first = raw.find("{")
    last = raw.rfind("}")

    if first == -1 or last == -1:
        return None

    json_text = raw[first : last + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None
