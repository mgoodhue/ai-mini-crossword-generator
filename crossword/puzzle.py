from .grid import CrosswordGrid, GridChanges
from .slot import Slot, SlotKind


class Puzzle:
    def __init__(self, grid: CrosswordGrid, min_slot_length: int = 3) -> None:
        self.grid: CrosswordGrid = grid
        self.min_slot_length: int = min_slot_length
        self.slots: list[Slot] = self._build_slots()
        self.used_slots: dict[tuple[SlotKind, int, int, int], str] = {}

    def _slot_key(self, slot: Slot) -> tuple[SlotKind, int, int, int]:
        return (slot.kind, slot.index, slot.start, slot.length)

    def _build_slots(self) -> list[Slot]:
        slots: list[Slot] = []
        size = self.grid.size

        for row in range(size):
            start = 0
            while start < size:
                while start < size and self.grid.is_block(row, start):
                    start += 1
                end = start
                while end < size and not self.grid.is_block(row, end):
                    end += 1
                run_length = end - start
                if run_length >= self.min_slot_length:
                    slots.append(
                        Slot(
                            kind=SlotKind.ROW,
                            index=row,
                            start=start,
                            length=run_length,
                            pattern="." * run_length,
                        )
                    )
                start = end + 1

        for col in range(size):
            start = 0
            while start < size:
                while start < size and self.grid.is_block(start, col):
                    start += 1
                end = start
                while end < size and not self.grid.is_block(end, col):
                    end += 1
                run_length = end - start
                if run_length >= self.min_slot_length:
                    slots.append(
                        Slot(
                            kind=SlotKind.COL,
                            index=col,
                            start=start,
                            length=run_length,
                            pattern="." * run_length,
                        )
                    )
                start = end + 1

        return slots

    def is_complete(self) -> bool:
        return len(self.used_slots) == len(self.slots)

    def available_slots(self) -> list[Slot]:
        slots: list[Slot] = []
        for slot in self.slots:
            key = self._slot_key(slot)
            if key in self.used_slots:
                continue
            slots.append(
                Slot(
                    kind=slot.kind,
                    index=slot.index,
                    start=slot.start,
                    length=slot.length,
                    pattern=self.grid.get_slot_pattern(slot),
                )
            )
        return slots

    def is_word_used(self, word: str) -> bool:
        return word in self.used_slots.values()

    def place(self, slot: Slot, word: str) -> GridChanges | None:
        changed = self.grid.place_slot(slot, word)
        if changed is None:
            return None
        self.used_slots[self._slot_key(slot)] = word
        return changed

    def undo_place(self, slot: Slot, changed: GridChanges) -> None:
        del self.used_slots[self._slot_key(slot)]
        self.grid.undo(changed)

    def words_by_kind(self, kind: SlotKind) -> list[str]:
        words_with_pos: list[tuple[int, int, str]] = []
        for slot in self.slots:
            if slot.kind != kind:
                continue
            key = self._slot_key(slot)
            if key in self.used_slots:
                words_with_pos.append((slot.index, slot.start, self.used_slots[key]))
        words_with_pos.sort(key=lambda x: (x[0], x[1]))
        return [word for _, _, word in words_with_pos]
