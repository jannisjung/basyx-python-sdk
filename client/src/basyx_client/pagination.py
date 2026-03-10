from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Page:
    def __init__(self, result: List[object], cursor: Optional[str] = None):
        self.result = result
        self.cursor = cursor

