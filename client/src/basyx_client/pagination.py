from dataclasses import dataclass


@dataclass
class Page:
    def __init__(self, result: list[object], cursor: str | None = None):
        self.result = result
        self.cursor = cursor

