"""Command handlers: /health, /labs, /scores."""

from config import settings
from services.api_client import LMSAPIClient


async def handle_health() -> str:
    """Check backend health by querying the LMS API."""
    client = LMSAPIClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    try:
        result = await client.health_check()
        return result["message"]
    finally:
        await client.close()


async def handle_labs() -> str:
    """List available labs (placeholder)."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


async def handle_scores() -> str:
    """Get scores for a lab (placeholder)."""
    return "Scores for lab: Task 1: 80%, Task 2: 75% (placeholder)"
