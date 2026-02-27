CellPosition = tuple[int, int]
GridChanges = list[CellPosition]

from .slot import Slot, SlotKind


class CrosswordGrid:
    def __init__(self, size: int, blocks: set[CellPosition] | None = None) -> None:
        self.size: int = size
        self.cells: list[list[str]] = [["." for _ in range(size)] for _ in range(size)]
        self.blocks: set[CellPosition] = set(blocks or set())
        for row, col in self.blocks:
            if row < 0 or col < 0 or row >= size or col >= size:
                raise ValueError(f"Block position out of bounds: {(row, col)}")
            self.cells[row][col] = "#"

    def is_block(self, row: int, col: int) -> bool:
        return self.cells[row][col] == "#"

    def get_row_pattern(self, row: int) -> str:
        return "".join(self.cells[row])

    def get_col_pattern(self, col: int) -> str:
        return "".join(self.cells[row][col] for row in range(self.size))

    def get_slot_pattern(self, slot: Slot) -> str:
        chars: list[str] = []
        for row, col in self._iter_slot_cells(slot):
            chars.append(self.cells[row][col])
        return "".join(chars)

    def _iter_slot_cells(self, slot: Slot) -> list[CellPosition]:
        if slot.kind == SlotKind.ROW:
            return [(slot.index, slot.start + offset) for offset in range(slot.length)]
        return [(slot.start + offset, slot.index) for offset in range(slot.length)]

    def place_slot(self, slot: Slot, word: str) -> GridChanges | None:
        if len(word) != slot.length:
            return None
        changed: GridChanges = []
        for (row, col), ch in zip(self._iter_slot_cells(slot), word):
            cell = self.cells[row][col]
            if cell == "#":
                return None
            if cell == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif cell != ch:
                return None
        return changed

    def place_row(self, row: int, word: str) -> GridChanges | None:
        if len(word) != self.size:
            return None
        changed: GridChanges = []
        for col, ch in enumerate(word):
            if self.cells[row][col] == "#":
                return None
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def place_col(self, col: int, word: str) -> GridChanges | None:
        if len(word) != self.size:
            return None
        changed: GridChanges = []
        for row, ch in enumerate(word):
            if self.cells[row][col] == "#":
                return None
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def undo(self, changed: GridChanges) -> None:
        for row, col in changed:
            if self.cells[row][col] != "#":
                self.cells[row][col] = "."

    def is_filled(self) -> bool:
        return all(
            self.cells[row][col] != "."
            for row in range(self.size)
            for col in range(self.size)
        )

    def to_lines(self) -> list[str]:
        return ["".join(row) for row in self.cells]
