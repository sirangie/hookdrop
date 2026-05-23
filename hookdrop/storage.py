"""In-memory storage for captured webhook requests."""

import uuid
from datetime import datetime, timezone
from typing import Optional


class WebhookRequest:
    def __init__(self, method: str, path: str, headers: dict, body: bytes, query_string: str = ""):
        self.id = str(uuid.uuid4())
        self.method = method
        self.path = path
        self.headers = dict(headers)
        self.body = body
        self.query_string = query_string
        self.received_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body.decode("utf-8", errors="replace"),
            "query_string": self.query_string,
            "received_at": self.received_at.isoformat(),
        }


class RequestStore:
    def __init__(self, max_requests: int = 200):
        self._requests: list[WebhookRequest] = []
        self.max_requests = max_requests

    def add(self, request: WebhookRequest) -> WebhookRequest:
        self._requests.append(request)
        if len(self._requests) > self.max_requests:
            self._requests.pop(0)
        return request

    def get_all(self) -> list[WebhookRequest]:
        return list(reversed(self._requests))

    def get_by_id(self, request_id: str) -> Optional[WebhookRequest]:
        for req in self._requests:
            if req.id == request_id:
                return req
        return None

    def clear(self) -> int:
        count = len(self._requests)
        self._requests.clear()
        return count

    def __len__(self) -> int:
        return len(self._requests)


# Global shared store instance
store = RequestStore()
