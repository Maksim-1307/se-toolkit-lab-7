"""
LMS Telegram Bot — Entry Point

Usage:
    uv run bot.py                    # Start Telegram bot
    uv run bot.py --test "/start"    # Test mode: call handler directly
    uv run bot.py --test "..."       # Test LLM intent routing for natural language
"""

import argparse
import asyncio
import logging
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.natural_language import handle_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Command registry: maps command name to handler function
# Handlers can be either Callable[[], Awaitable[str]] or Callable[[str], Awaitable[str]]
_command_registry: dict[str, Callable] = {}


def register_command(name: str) -> Callable:
    """
    Decorator to register a command handler.

    Usage:
        @register_command("start")
        async def handle_start() -> str:
            return "Welcome!"
    """
    def decorator(func: Callable) -> Callable:
        _command_registry[name] = func
        return func
    return decorator


def get_handler(command: str) -> Callable | None:
    """Get handler function by command name."""
    return _command_registry.get(command)


async def run_test_mode(input_text: str) -> None:
    """
    Test mode: run a command handler or LLM router based on input.
    
    - If input starts with '/', treat as a command
    - Otherwise, route through LLM for natural language processing
    
    Debug output goes to stderr.
    """
    import sys
    
    # Check if this is a command (starts with /)
    if input_text.startswith("/"):
        # Parse command (e.g., "/start" -> "start", "/scores lab-04" -> "scores")
        parts = input_text.lstrip("/").split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        handler = get_handler(cmd)
        if handler is None:
            print(f"Unknown command: {input_text}")
            print("Use /help to see available commands.")
            return

        try:
            # Call handler with args if it accepts them
            import inspect
            sig = inspect.signature(handler)
            if len(sig.parameters) > 0:
                response = await handler(*args)
            else:
                response = await handler()
            print(response)
        except TypeError as e:
            if "missing" in str(e):
                print(f"Error: Command '{cmd}' requires arguments. Usage: /{cmd} <arg>")
            else:
                print(f"Error executing command: {e}")
                raise
        except Exception as e:
            print(f"Error executing command: {e}")
            raise
    else:
        # Natural language message - route through LLM
        print(f"[llm] Processing: {input_text}", file=sys.stderr)
        try:
            response = await handle_message(input_text, debug=True)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            raise


async def run_telegram_mode() -> None:
    """Start the Telegram bot and listen for messages."""
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Helper to send response with optional keyboard
    async def send_response(message: types.Message, response) -> None:
        """Send response handling both tuple (text, keyboard) and plain text."""
        if isinstance(response, tuple):
            text, keyboard = response
            await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(response)

    # Register all commands with aiogram
    for cmd_name, handler_func in _command_registry.items():
        # Create a wrapper that calls our handler and sends the response
        async def command_wrapper(message: types.Message, cmd=cmd_name) -> None:
            try:
                handler = _command_registry[cmd]
                # Extract arguments from message text (e.g., "/scores lab-01" -> ["lab-01"])
                parts = message.text.split()[1:] if message.text else []
                import inspect
                sig = inspect.signature(handler)
                if len(sig.parameters) > 0:
                    response = await handler(*parts)
                else:
                    response = await handler()
                await send_response(message, response)
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                await message.answer("Sorry, something went wrong.")

        # Register with aiogram's command filter
        dp.message.register(command_wrapper, Command(cmd_name))

    # Handle callback queries from inline buttons
    async def handle_callback(callback: types.CallbackQuery) -> None:
        """Handle inline button callback queries."""
        data = callback.data
        message = callback.message
        
        try:
            if data == "quick_labs":
                response = await handle_labs()
                await message.answer(response)
            elif data == "quick_health":
                response = await handle_health()
                await message.answer(response)
            elif data == "quick_scores":
                await message.answer("Please specify a lab, e.g., 'lab-01' or use /scores lab-01")
            elif data == "quick_top":
                await message.answer("Please specify a lab for top students, e.g., 'Show top 5 in lab-01'")
            elif data == "quick_help":
                response = await handle_help()
                await message.answer(response)
            elif data == "back":
                await message.answer("Use /start to see main menu")
            
            # Acknowledge the callback
            await callback.answer()
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await callback.answer("Sorry, something went wrong.")

    dp.callback_query.register(handle_callback)

    # Handle all other text messages with the LLM intent router
    async def handle_text_message(message: types.Message) -> None:
        try:
            # Skip if this is a command (starts with /)
            if message.text and message.text.startswith("/"):
                return

            response = await handle_message(message.text, debug=False)
            await message.answer(response)
        except Exception as e:
            logger.error(f"Error in LLM routing: {e}")
            await message.answer("Sorry, I'm having trouble understanding that right now.")

    dp.message.register(handle_text_message)

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
        metavar="INPUT",
        help="Test mode: run a command handler (--test '/start') or LLM routing (--test 'what labs...')"
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler or LLM router
        asyncio.run(run_test_mode(args.test))
    else:
        # Normal mode: start Telegram bot
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
