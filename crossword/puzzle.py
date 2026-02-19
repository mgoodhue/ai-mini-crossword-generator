class Puzzle:
    def __init__(self, grid):
        self.grid = grid
        self.used_rows = {}
        self.used_cols = {}

    def is_complete(self, size):
        return len(self.used_rows) == size and len(self.used_cols) == size

    def available_slots(self, size):
        slots = []
        for row in range(size):
            if row not in self.used_rows:
                slots.append(("row", row, self.grid.get_row_pattern(row)))
        for col in range(size):
            if col not in self.used_cols:
                slots.append(("col", col, self.grid.get_col_pattern(col)))
        return slots

    def is_word_used(self, word):
        return word in self.used_rows.values() or word in self.used_cols.values()

    def place(self, kind, idx, word):
        if kind == "row":
            changed = self.grid.place_row(idx, word)
            if changed is None:
                return None
            self.used_rows[idx] = word
            return changed

        changed = self.grid.place_col(idx, word)
        if changed is None:
            return None
        self.used_cols[idx] = word
        return changed

    def undo_place(self, kind, idx, changed):
        if kind == "row":
            del self.used_rows[idx]
        else:
            del self.used_cols[idx]
        self.grid.undo(changed)

