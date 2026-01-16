from typing import Any
import httpx


async def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> httpx.Response:
    """
    Sends a JSON payload using a short-lived HTTP client.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.post(url, headers=headers, json=payload)
