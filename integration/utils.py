import dataclasses
from typing import Any


@dataclasses.dataclass
class StatusCode:
    SUCCESS: int = 200
    FAILED: int = 400


@dataclasses.dataclass
class Response:
    status_code: int
    data: dict[str, Any]
