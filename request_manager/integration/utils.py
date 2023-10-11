import dataclasses
import enum
from typing import Any


class StatusCode(enum.IntEnum):
    SUCCESS: int = 200
    FAILED: int = 400


@dataclasses.dataclass
class Response:
    status_code: int
    data: dict[str, Any]


class CLIActions(enum.StrEnum):
    WIZARD = "Wizard"
    RUN = "Start providers"
    STOP = "Stop providers"
    SIMULATE_EXAMPLE = "Simulate example"
    ADD_PROVIDER = "Add new provider"
    ENABLE_PROVIDER = "Enable provider"
    DISABLE_PROVIDER = "Disable provider"
    ADD_REQUEST = "Add new request"
    EXIT = "Exit program"
