# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with API keys (see `.env.example`):
```
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## Running

```bash
python main.py
# or with a custom config:
python main.py --config settings/config.yaml
# or on Windows:
run.bat
```

There are no automated tests or linting configured.

## Architecture

This is a Python async batch utility that sends large volumes of prompts to OpenAI, Anthropic, and Google LLM APIs concurrently, writing each response to a JSON file.

**Data flow:**
1. `main.py` loads `settings/config.yaml`, reads the CSV input, system prompt text file, and scans for images
2. `src/validator.py:validate_csv()` checks the CSV schema and image references
3. `src/utils.py:add_tasks()` builds a list of async coroutines, routing each row by `model` column value to the appropriate provider module
4. Tasks are chunked into batches (`batch_size` from config) and run with `asyncio.gather()`
5. Each provider module (`src/call_openai.py`, `src/call_anthropic.py`, `src/call_google.py`) handles auth, base64 image encoding, and error handling, then writes output JSON to `output/`

**Model routing in `src/utils.py`:**
- `"gpt"` in model name → `call_openai.call_gpt()`
- `"claude"` in model name → `call_anthropic.call_claude()`
- `"gemini"` in model name → `call_google.call_gemini()`

**CSV input columns:** `model`, `save_path`, `user_prompt` (optional), `image_path` (optional)

**Key config (`settings/config.yaml`):**
- `path.input`: CSV file path
- `path.system_prompt`: System prompt `.txt` file
- `path.output`: Output folder for JSON results
- `settings.request.batch_size`: Number of concurrent requests (default 50)
- `settings.image_file.base_root`: Root folder for images

Logs are written daily to `logs/{date}.log`.
