from dataclasses import dataclass
from enum import Enum


class SlotKind(str, Enum):
    ROW = "row"
    COL = "col"


@dataclass(frozen=True)
class Slot:
    kind: SlotKind
    index: int
    start: int
    length: int
    pattern: str
