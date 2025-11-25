# Running the LLM model Locally

This project uses Ollama model as the local LLM runtime for interpreting natural-language backtest prompts.

## 1. Install Ollama

Download and install Ollama from the official website:

 https://ollama.com/download

Supported OS: macOS, Linux, Windows (WSL & native Windows support)
This guide assumes **Windows 11** as supported OS

## 2. Open the terminal 

### Windows:

Open PowerShell
Press: Win + X → Windows PowerShell

### Mac:

Open Terminal (Finder → Applications → Utilities → Terminal)

### Linux:

Open your standard terminal.

- All commands below must be run in PowerShell or Terminal, not inside Python, VSCode or Docker

## 3. Verify that Ollama Installed Correctly

Once installed, on Windows - Ollama automatically runs in the background as a system service.

In Powershell:
```bash
ollama --version
```
Expected output Example:
```bash
ollama version 0.1.36
```

Check installed models:
```bash
ollama list
```
If Ollama is installed but no models downloaded, nothing is showed

If you see no error and a list of models (or empty list), the Ollama server is running.

## 4. Download the required model

This project uses **llama3:8b**, which gives accurate structured JSON output for backtest.

Download it in powershell:
```bash
ollama pull llama3:8b
```
This will take a few minutes (model is ~4.7 GB).

Expected Final output:
```bash
pulling manifest
pulling 4.7 GB model
success
```

You can check the HTTP API:
```bash
curl http://127.0.0.1:11434/api/tags
```

You should get a JSON response that looks like:
```json
{"models": [{"name":"llama3:8b", ...}]}
```

## 5. Run the model manually (test it) - Important

You can try chatting with the model:
In Powershell:
```bash
ollama run llama3:8b
```

Type anything to ensure the model works.

Exit with:
```bash
/bye
```

## 6. Check that the API works (required for FastAPI)

The application calls Ollama via HTTP, so ensure this works:
In Powershell/Terminal:
```bash
curl -X POST http://127.0.0.1:11434/api/generate \
    -d '{"model":"llama3:8b", "prompt":"hello"}'
```

Expected Output:
```json
{
  "models": [
    {
      "name": "llama3:8b",
      "size": 4661224676
    }
  ]
}
```

You should get a JSON response - API Running properly

## 7. Test the LLM API With a Prompt (critical)

In Powershell run:
```bash
curl -X POST http://127.0.0.1:11434/api/generate `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"llama3:8b\",\"prompt\":\"hello world\"}"
```

Expected output:
```json
{"model":"llama3:8b","response":"Hello! ..."}
```
If this works → your LLM is fully operational.

## 8. Environment variable 

The application uses this default:

OLLAMA_HOST=http://127.0.0.1:11434


You only need to set this if you change the port or run inside Docker.

## 9. Start the FastAPI server

Once Ollama is running normally:
In IDE Terminal where in project present:
```bash
uvicorn app.main:app --reload
```

Now the prompt-based endpoint will successfully call the LLM.


