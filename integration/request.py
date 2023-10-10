import datetime
import time


class Request:
    def __init__(
        self,
        provider: "Provider",
        priority: int,
        execution_after: datetime.datetime | int = 0,
        name: str = "",
    ):
        self.name = name
        self.provider = provider
        self.retry_count = 0
        # for use in PriorityQueue we must invert the priority to act as a max-heap
        self.priority = priority * -1
        if isinstance(execution_after, datetime.datetime):
            self.execution_time = execution_after.timestamp()
        elif isinstance(execution_after, int):
            self.execution_time = time.time() + execution_after

    def __repr__(self):
        return (
            f"Request(name={self.name}, priority={self.priority * -1},"
            f" execution_time={datetime.datetime.fromtimestamp(self.execution_time).strftime('%H:%M:%S')},"
            f" provider={self.provider.name})"
        )

    def __lt__(self, other: "Request"):
        return self.priority < other.priority

    @property
    def is_ready(self) -> bool:
        return time.time() >= self.execution_time
