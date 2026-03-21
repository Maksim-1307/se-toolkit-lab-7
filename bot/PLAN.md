# LMS Telegram Bot — Development Plan

## What We're Building

A Telegram bot that lets users interact with the LMS backend through chat. Users can check system health, browse labs and scores, and ask questions in plain language. The bot uses an LLM to understand what the user wants and fetch the right data.

## Architecture

The key idea is **testable handlers** — command logic is just plain functions that take input and return text. They don't know about Telegram. The same handler works from:
- `--test` mode (CLI testing)
- Unit tests
- The actual Telegram bot

This is called **separation of concerns**. It means you can test your logic without needing a Telegram connection.

## Task 1: Plan and Scaffold

Create the project skeleton:

1. **`bot/bot.py`** — Entry point with `--test` mode
   - `uv run bot.py --test "/start"` prints response to stdout
   - Normal mode starts the Telegram bot

2. **`bot/handlers/`** — Command handlers (no Telegram dependency)
   - `/start`, `/help`, `/health`, `/labs`, `/scores`
   - Each returns placeholder text initially

3. **`bot/config.py`** — Load env vars from `.env.bot.secret`

4. **`bot/pyproject.toml`** — Dependencies: `aiogram`, `httpx`, `pydantic-settings`

5. **`.env.bot.secret`** — Secrets: `BOT_TOKEN`, `LMS_API_BASE_URL`, `LMS_API_KEY`

## Task 2: Backend Integration

Connect handlers to the real LMS API:

1. **`bot/services/lms_client.py`** — API client wrapper
   - Bearer token auth for all requests
   - Methods: `get_health()`, `get_labs()`, `get_scores(lab_id)`
   - Handle errors gracefully (timeouts, 401, 500)

2. **Update handlers** to call the service instead of returning placeholders

3. **Error handling** — backend down shows friendly message, not a crash

## Task 3: Intent-Based Natural Language Routing

Let users ask questions in plain language:

1. **`bot/services/llm_client.py`** — LLM wrapper with tool calling

2. **Define tools** for the LLM:
   - `get_health()` — check system status
   - `get_labs()` — list available labs
   - `get_scores(lab_id)` — get scores for a lab

3. **Intent router** — user sends plain text → LLM picks the right tool → bot executes and returns result

The LLM reads tool descriptions to decide which to call. Description quality matters more than prompt engineering.

## Task 4: Containerize and Document

Deploy the bot with Docker:

1. **`bot/Dockerfile`** — Python 3.14 slim base, install with `uv`

2. **Update `docker-compose.yml`** — add bot service with env vars

3. **Docker networking** — containers use service names, not `localhost`
   - Backend URL becomes `http://backend:42002` inside the bot container

4. **Documentation** — README with deployment instructions

## File Structure

```
bot/
├── bot.py              # Entry point
├── config.py           # Config loading
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── handlers/
│   └── commands.py     # Command handlers
└── services/
    ├── lms_client.py   # Backend API (Task 2)
    └── llm_client.py   # LLM client (Task 3)
```

## Testing

```bash
cd bot
uv sync
uv run bot.py --test "/start"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
```

Each command should print something and exit with code 0.

## Git Workflow

For each task:
1. Create issue
2. Branch: `git checkout -b task-1-scaffold`
3. Implement, test, commit
4. PR with `Closes #...`
5. Partner review, merge
