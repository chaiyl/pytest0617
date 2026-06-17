from typing import Any

import requests

from utils.http_client import HttpClient


class TicketService:
    """Encapsulate ticket-related API calls."""

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    def get_ticket_info(self, payload: dict[str, Any]) -> requests.Response:
        return self.client.post("/get-ticket-info", json=payload)
