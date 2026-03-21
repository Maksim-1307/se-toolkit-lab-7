"""
LMS Telegram Bot — Entry Point

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: call handler directly
"""

import argparse
import asyncio
import logging
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Command registry: maps command name to handler function
_command_registry: dict[str, Callable[[], Awaitable[str]]] = {}


def register_command(name: str) -> Callable:
    """
    Decorator to register a command handler.
    
    Usage:
        @register_command("start")
        async def handle_start() -> str:
            return "Welcome!"
    """
    def decorator(func: Callable[[], Awaitable[str]]) -> Callable:
        _command_registry[name] = func
        return func
    return decorator


def get_handler(command: str) -> Callable[[], Awaitable[str]] | None:
    """Get handler function by command name."""
    return _command_registry.get(command)


async def run_test_mode(command: str) -> None:
    """
    Run a command handler directly and print result to stdout.
    
    This bypasses Telegram entirely — useful for testing handlers
    without needing a bot token or network connection.
    """
    # Parse command (e.g., "/start" -> "start", "/scores lab-04" -> "scores")
    cmd = command.lstrip("/").split()[0]
    
    handler = get_handler(cmd)
    if handler is None:
        print(f"Error: Unknown command '{command}'")
        print("Available commands:", ", ".join(_command_registry.keys()))
        return
    
    try:
        response = await handler()
        print(response)
    except Exception as e:
        print(f"Error executing command: {e}")
        raise


async def run_telegram_mode() -> None:
    """Start the Telegram bot and listen for messages."""
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register all commands with aiogram
    for cmd_name, handler_func in _command_registry.items():
        # Create a wrapper that calls our handler and sends the response
        async def command_wrapper(message: types.Message, cmd=cmd_name) -> None:
            try:
                handler = _command_registry[cmd]
                response = await handler()
                await message.answer(response)
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                await message.answer("Sorry, something went wrong.")

        # Register with aiogram's command filter
        dp.message.register(command_wrapper, Command(cmd_name))

    logger.info("Starting bot...")
    await dp.start_polling(bot)


# =============================================================================
# Register Commands
# =============================================================================

register_command("start")(handle_start)
register_command("help")(handle_help)
register_command("health")(handle_health)
register_command("labs")(handle_labs)
register_command("scores")(handle_scores)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Test mode: run a command handler directly (e.g., --test '/start')"
    )
    args = parser.parse_args()
    
    if args.test:
        # Test mode: call handler directly
        asyncio.run(run_test_mode(args.test))
    else:
        # Normal mode: start Telegram bot
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
