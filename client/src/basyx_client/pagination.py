from dataclasses import dataclass
from typing import List


@dataclass
class Page:
    def __init__(self, result: List[object], cursor: str):
        self.result = result
        self.cursor = cursor
