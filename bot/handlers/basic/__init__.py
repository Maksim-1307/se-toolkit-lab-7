"""Basic command handlers: /start, /help."""

from config import settings


def _get_bot_name() -> str:
    """Extract bot name from the bot token.
    
    Telegram bot tokens have format: <bot_id>:<token>
    The bot name is typically the bot_id part (e.g., 'MyBot' from 'MyBot:abc123...').
    """
    bot_token = settings.bot_token
    if ":" in bot_token:
        return bot_token.split(":")[0]
    return "LMS Bot"


async def handle_start() -> str:
    """Welcome message with bot name."""
    bot_name = _get_bot_name()
    return (
        f"Welcome to {bot_name}!\n\n"
        "I can help you check your LMS labs and scores.\n"
        "Use /help to see available commands."
    )


async def handle_help() -> str:
    """List all available commands with descriptions."""
    return (
        "Available commands:\n\n"
        "  /start — Welcome message\n"
        "  /help — Show this help message\n"
        "  /health — Check if the LMS backend is running\n"
        "  /labs — List all available labs\n"
        "  /scores <lab> — Get your scores for a specific lab"
    )
