"""Natural language intent handler using LLM routing."""

from services.intent_router import route


async def handle_message(text: str, debug: bool = False) -> str:
    """
    Handle a natural language message using the LLM intent router.
    
    Args:
        text: The user's message text
        debug: If True, enable debug logging
        
    Returns:
        The LLM's response
    """
    return await route(text, debug=debug)
