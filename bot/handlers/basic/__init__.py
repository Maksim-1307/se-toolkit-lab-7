"""Basic command handlers: /start, /help."""


async def handle_start() -> str:
    """Welcome message."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    """List available commands."""
    return (
        "Available commands:\n"
        "  /start — Welcome message\n"
        "  /help — Show this help\n"
        "  /health — Check backend status\n"
        "  /labs — List available labs\n"
        "  /scores <lab> — Get scores for a lab"
    )
