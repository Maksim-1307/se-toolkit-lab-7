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
    """List all available labs from the LMS API."""
    client = LMSAPIClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    try:
        result = await client.get_labs()
        if not result["ok"]:
            return f"Error: {result['error']}"
        
        labs = result["labs"]
        if not labs:
            return "No labs available."
        
        # Format lab titles as a numbered list
        lab_list = "\n".join(
            f"  {i + 1}. {lab['title']}"
            for i, lab in enumerate(labs)
        )
        return f"Available labs:\n\n{lab_list}"
    finally:
        await client.close()


async def handle_scores(lab: str = "") -> str:
    """Get per-task scores for a specific lab.
    
    Args:
        lab: The lab identifier (e.g., 'lab-01').
    """
    if not lab:
        return "Please specify a lab. Usage: /scores <lab>\nExample: /scores lab-01"
    
    client = LMSAPIClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )
    try:
        result = await client.get_scores(lab)
        if not result["ok"]:
            return f"Error: {result['error']}"
        
        scores = result["scores"]
        if not scores:
            return f"No scores found for lab '{lab}'."
        
        # Format per-task scores
        score_lines = []
        for task_score in scores:
            # Handle different response formats
            if isinstance(task_score, dict):
                task_name = task_score.get("task", task_score.get("name", "Unknown"))
                pass_rate = task_score.get("avg_score")
                # Convert to percentage if it's a decimal
                if isinstance(pass_rate, float) and pass_rate <= 1:
                    pass_rate = pass_rate * 100
                score_lines.append(f"  {task_name}: {pass_rate:.1f}%")
            else:
                score_lines.append(f"  {task_score}")
        
        return f"Scores for {lab}:\n\n" + "\n".join(score_lines)
    finally:
        await client.close()
