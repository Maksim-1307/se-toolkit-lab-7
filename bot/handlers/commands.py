"""Basic command handlers: /start, /help, /health, /labs, /scores."""


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


async def handle_health() -> str:
    """Check backend health (placeholder)."""
    return "Backend status: OK (placeholder)"


async def handle_labs() -> str:
    """List available labs (placeholder)."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


async def handle_scores() -> str:
    """Get scores for a lab (placeholder)."""
    return "Scores for lab: Task 1: 80%, Task 2: 75% (placeholder)"
