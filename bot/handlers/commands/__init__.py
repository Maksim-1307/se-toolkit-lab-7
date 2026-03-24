"""Command handlers: /health, /labs, /scores."""


async def handle_health() -> str:
    """Check backend health (placeholder)."""
    return "Backend status: OK (placeholder)"


async def handle_labs() -> str:
    """List available labs (placeholder)."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


async def handle_scores() -> str:
    """Get scores for a lab (placeholder)."""
    return "Scores for lab: Task 1: 80%, Task 2: 75% (placeholder)"
