"""Basic command handlers: /start, /help."""

from aiogram.types import InlineKeyboardMarkup

from config import settings
from keyboards import get_quick_actions_keyboard


def _get_bot_name() -> str:
    """Extract bot name from the bot token.

    Telegram bot tokens have format: <bot_id>:<token>
    The bot name is typically the bot_id part (e.g., 'MyBot' from 'MyBot:abc123...').
    """
    bot_token = settings.bot_token
    if ":" in bot_token:
        return bot_token.split(":")[0]
    return "LMS Bot"


async def handle_start() -> tuple[str, InlineKeyboardMarkup]:
    """Welcome message with bot name and quick action buttons."""
    bot_name = _get_bot_name()
    text = (
        f"Welcome to {bot_name}!\n\n"
        "I can help you check your LMS labs and scores.\n"
        "You can type questions in plain English, like:\n"
        "• 'Which lab has the lowest pass rate?'\n"
        "• 'Show me scores for lab 4'\n"
        "• 'Who are the top 5 students?'\n\n"
        "Or use the buttons below!"
    )
    keyboard = get_quick_actions_keyboard()
    return text, keyboard


async def handle_help() -> str:
    """List all available commands with descriptions."""
    return (
        "Available commands:\n\n"
        "  /start — Welcome message\n"
        "  /help — Show this help message\n"
        "  /health — Check if the LMS backend is running\n"
        "  /labs — List all available labs\n"
        "  /scores <lab> — Get your scores for a specific lab\n\n"
        "You can also type natural language questions like:\n"
        "• 'what labs are available?'\n"
        "• 'which lab has the best scores?'\n"
        "• 'show me the top 10 students'"
    )
