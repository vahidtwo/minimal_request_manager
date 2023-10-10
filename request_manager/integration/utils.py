import dataclasses
import enum
from typing import Any


@dataclasses.dataclass
class StatusCode:
    SUCCESS: int = 200
    FAILED: int = 400


@dataclasses.dataclass
class Response:
    status_code: int
    data: dict[str, Any]


class CLIActions(enum.StrEnum):
    SIMULATE = "simulate and start jobs"
    RUN = "start jobs"
    ADD_PROVIDER = "add new provider"
    START_PROVIDER = "start provider"
    STOP_PROVIDER = "stop provider"
    ADD_REQUEST = "add request"
    EXIT = "exit program"
