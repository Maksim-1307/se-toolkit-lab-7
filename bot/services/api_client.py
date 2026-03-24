"""LMS API client for the Telegram bot."""

import httpx


class LMSAPIClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

    async def health_check(self) -> dict:
        """
        Check backend health by querying /items endpoint.

        Returns:
            dict with keys:
                - ok (bool): True if backend is healthy
                - status_code (int | None): HTTP status code if available
                - message (str): Human-readable status message
        """
        url = f"{self.base_url}/items/"
        try:
            response = await self._client.get(url)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "message": "Backend is healthy",
                }
            else:
                return {
                    "ok": False,
                    "status_code": response.status_code,
                    "message": self._get_error_message(response.status_code),
                }
        except httpx.ConnectError:
            return {
                "ok": False,
                "status_code": None,
                "message": "Unable to connect to the backend. Please check if the service is running.",
            }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "status_code": None,
                "message": "Backend request timed out. The service may be overloaded.",
            }
        except Exception:
            return {
                "ok": False,
                "status_code": None,
                "message": "An unexpected error occurred while checking backend status.",
            }

    def _get_error_message(self, status_code: int) -> str:
        """Return a user-friendly message for an HTTP status code."""
        messages = {
            400: "Bad Gateway (400): The backend received an invalid request.",
            401: "Unauthorized (401): API key is missing or invalid.",
            403: "Forbidden (403): Access denied. Check API key permissions.",
            404: "Not Found (404): The requested resource does not exist.",
            500: "Internal Server Error (500): The backend encountered an error.",
            502: "Bad Gateway (502): The backend service may be down or unreachable.",
            503: "Service Unavailable (503): The backend is temporarily unavailable.",
            504: "Gateway Timeout (504): The backend took too long to respond.",
        }
        return messages.get(
            status_code,
            f"Backend error: HTTP {status_code}. Please try again later.",
        )

    async def close(self):
        """Close the HTTP client session."""
        await self._client.aclose()
