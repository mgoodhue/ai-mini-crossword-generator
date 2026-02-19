CellPosition = tuple[int, int]
GridChanges = list[CellPosition]


class CrosswordGrid:
    def __init__(self, size: int) -> None:
        self.size: int = size
        self.cells: list[list[str]] = [["." for _ in range(size)] for _ in range(size)]

    def get_row_pattern(self, row: int) -> str:
        return "".join(self.cells[row])

    def get_col_pattern(self, col: int) -> str:
        return "".join(self.cells[row][col] for row in range(self.size))

    def place_row(self, row: int, word: str) -> GridChanges | None:
        changed: GridChanges = []
        for col, ch in enumerate(word):
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def place_col(self, col: int, word: str) -> GridChanges | None:
        changed: GridChanges = []
        for row, ch in enumerate(word):
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def undo(self, changed: GridChanges) -> None:
        for row, col in changed:
            self.cells[row][col] = "."

    def is_filled(self) -> bool:
        return all(
            self.cells[row][col] != "."
            for row in range(self.size)
            for col in range(self.size)
        )

    def to_lines(self) -> list[str]:
        return ["".join(row) for row in self.cells]
