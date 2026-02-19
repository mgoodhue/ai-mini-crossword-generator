class CrosswordGrid:
    def __init__(self, size):
        self.size = size
        self.cells = [["." for _ in range(size)] for _ in range(size)]

    def get_row_pattern(self, row):
        return "".join(self.cells[row])

    def get_col_pattern(self, col):
        return "".join(self.cells[row][col] for row in range(self.size))

    def place_row(self, row, word):
        changed = []
        for col, ch in enumerate(word):
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def place_col(self, col, word):
        changed = []
        for row, ch in enumerate(word):
            if self.cells[row][col] == ".":
                self.cells[row][col] = ch
                changed.append((row, col))
            elif self.cells[row][col] != ch:
                return None
        return changed

    def undo(self, changed):
        for row, col in changed:
            self.cells[row][col] = "."

    def is_filled(self):
        return all(
            self.cells[row][col] != "."
            for row in range(self.size)
            for col in range(self.size)
        )

    def to_lines(self):
        return ["".join(row) for row in self.cells]
