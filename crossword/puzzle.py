from .grid import CrosswordGrid, GridChanges
from .slot import Slot, SlotKind


class Puzzle:
    def __init__(self, grid: CrosswordGrid) -> None:
        self.grid: CrosswordGrid = grid
        self.used_rows: dict[int, str] = {}
        self.used_cols: dict[int, str] = {}

    def is_complete(self, size: int) -> bool:
        return len(self.used_rows) == size and len(self.used_cols) == size

    def available_slots(self, size: int) -> list[Slot]:
        slots: list[Slot] = []
        for row in range(size):
            if row not in self.used_rows:
                slots.append(Slot(SlotKind.ROW, row, self.grid.get_row_pattern(row)))
        for col in range(size):
            if col not in self.used_cols:
                slots.append(Slot(SlotKind.COL, col, self.grid.get_col_pattern(col)))
        return slots

    def is_word_used(self, word: str) -> bool:
        return word in self.used_rows.values() or word in self.used_cols.values()

    def place(self, slot: Slot, word: str) -> GridChanges | None:
        if slot.kind == SlotKind.ROW:
            changed = self.grid.place_row(slot.index, word)
            if changed is None:
                return None
            self.used_rows[slot.index] = word
            return changed

        changed = self.grid.place_col(slot.index, word)
        if changed is None:
            return None
        self.used_cols[slot.index] = word
        return changed

    def undo_place(self, slot: Slot, changed: GridChanges) -> None:
        if slot.kind == SlotKind.ROW:
            del self.used_rows[slot.index]
        else:
            del self.used_cols[slot.index]
        self.grid.undo(changed)
