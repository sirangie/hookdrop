import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


class WebhookRequest:
    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: str,
        query_string: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.method = method.upper()
        self.path = path
        self.headers = dict(headers)
        self.body = body
        self.query_string = query_string
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.tags: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "query_string": self.query_string,
            "timestamp": self.timestamp,
            "tags": self.tags,
        }


class RequestStore:
    def __init__(self, max_requests: int = 200):
        self._requests: List[WebhookRequest] = []
        self.max_requests = max_requests

    def add(self, req: WebhookRequest) -> WebhookRequest:
        self._requests.append(req)
        if len(self._requests) > self.max_requests:
            self._requests = self._requests[-self.max_requests :]
        return req

    def all(self) -> List[WebhookRequest]:
        return list(reversed(self._requests))

    def get(self, request_id: str) -> Optional[WebhookRequest]:
        for req in self._requests:
            if req.id == request_id:
                return req
        return None

    def clear(self):
        self._requests.clear()

    def count(self) -> int:
        return len(self._requests)
