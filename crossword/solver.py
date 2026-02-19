import random
from abc import ABC, abstractmethod

from .dictionary import WordRepository
from .puzzle import Puzzle
from .slot import Slot


class SlotHeuristic(ABC):
    @abstractmethod
    def pick(
        self, slots: list[Slot], repository: WordRepository
    ) -> tuple[Slot | None, list[int] | None]:
        raise NotImplementedError


class MinimumRemainingValuesHeuristic(SlotHeuristic):
    def pick(
        self, slots: list[Slot], repository: WordRepository
    ) -> tuple[Slot | None, list[int] | None]:
        best_slot: Slot | None = None
        best_candidates: list[int] | None = None

        for slot in slots:
            candidates = repository.pattern_candidates(slot.pattern)
            if (
                best_slot is None
                or best_candidates is None
                or len(candidates) < len(best_candidates)
            ):
                best_slot = slot
                best_candidates = candidates
            if best_candidates is not None and len(best_candidates) == 0:
                return best_slot, best_candidates

        return best_slot, best_candidates


class RandomSlotHeuristic(SlotHeuristic):
    def pick(
        self, slots: list[Slot], repository: WordRepository
    ) -> tuple[Slot | None, list[int] | None]:
        if not slots:
            return None, None

        slot = random.choice(slots)
        return slot, repository.pattern_candidates(slot.pattern)


class CrosswordSolver:
    def __init__(
        self, size: int, repository: WordRepository, heuristic: str = "mrv"
    ) -> None:
        self.size: int = size
        self.repository: WordRepository = repository
        self.heuristic: str = heuristic
        self.heuristics: dict[str, SlotHeuristic] = {
            "mrv": MinimumRemainingValuesHeuristic(),
            "random": RandomSlotHeuristic(),
        }

    def solve(self, puzzle: Puzzle) -> bool:
        if puzzle.is_complete(self.size):
            return True

        slots = puzzle.available_slots(self.size)

        strategy = self.heuristics.get(self.heuristic)
        if strategy is None:
            raise ValueError(
                f"Unknown heuristic '{self.heuristic}'. "
                "Expected one of: mrv, random."
            )

        best, best_candidates = strategy.pick(slots, self.repository)
        if best is None or best_candidates is None:
            return False
        if len(best_candidates) == 0:
            return False

        random.shuffle(best_candidates)

        for word_idx in best_candidates:
            word = self.repository.words[word_idx]

            if puzzle.is_word_used(word):
                continue

            changed = puzzle.place(best, word)
            if changed is None:
                continue
            if self.solve(puzzle):
                return True
            puzzle.undo_place(best, changed)

        return False
