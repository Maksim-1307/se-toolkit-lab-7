"""LLM client with tool calling support for the Telegram bot."""

import json
import httpx
from typing import Any


class LLMClient:
    """Client for interacting with LLM APIs using OpenAI-compatible format."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def _build_tool_definitions(self) -> list[dict]:
        """
        Build tool/function definitions for the LLM.
        
        These define what tools the LLM can call and their parameters.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "List all labs and tasks available in the system",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "List all enrolled learners and their groups",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a specific lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline (submissions per day) for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group scores and student counts for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01'",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top learners to return (default: 10)",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g., 'lab-01'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Refresh data from the autochecker system",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """
        Send a chat completion request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            tools: Optional list of tool definitions for function calling.

        Returns:
            dict with keys:
                - ok (bool): True if request succeeded
                - response (str | None): LLM response text
                - tool_calls (list[dict] | None): Tool calls from LLM
                - error (str | None): Error message if request failed
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            response = await self._client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                result = {
                    "ok": True,
                    "response": message.get("content"),
                    "tool_calls": None,
                    "error": None,
                }
                
                # Check for tool calls
                if message.get("tool_calls"):
                    result["tool_calls"] = [
                        {
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        }
                        for tc in message["tool_calls"]
                    ]
                
                return result
            elif response.status_code == 401:
                return {
                    "ok": False,
                    "response": None,
                    "tool_calls": None,
                    "error": "LLM API authentication failed. Check your API key.",
                }
            else:
                return {
                    "ok": False,
                    "response": None,
                    "tool_calls": None,
                    "error": f"LLM API error: HTTP {response.status_code}",
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "response": None,
                "tool_calls": None,
                "error": "Unable to connect to LLM service. Please check if it's running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "response": None,
                "tool_calls": None,
                "error": "LLM request timed out. The service may be overloaded.",
            }
        except json.JSONDecodeError as e:
            return {
                "ok": False,
                "response": None,
                "tool_calls": None,
                "error": f"Failed to parse LLM response: {e}",
            }
        except Exception as e:
            return {
                "ok": False,
                "response": None,
                "tool_calls": None,
                "error": f"Unexpected error: {e}",
            }

    async def close(self):
        """Close the HTTP client session."""
        await self._client.aclose()
