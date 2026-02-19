import random
from abc import ABC, abstractmethod


class SlotHeuristic(ABC):
    @abstractmethod
    def pick(self, slots, repository):
        raise NotImplementedError


class MinimumRemainingValuesHeuristic(SlotHeuristic):
    def pick(self, slots, repository):
        best_slot = None
        best_candidates = None

        for kind, idx, pattern in slots:
            candidates = repository.pattern_candidates(pattern)
            if best_slot is None or len(candidates) < len(best_candidates):
                best_slot = (kind, idx)
                best_candidates = candidates
            if best_candidates is not None and len(best_candidates) == 0:
                return best_slot, best_candidates

        return best_slot, best_candidates


class RandomSlotHeuristic(SlotHeuristic):
    def pick(self, slots, repository):
        if not slots:
            return None, None

        kind, idx, pattern = random.choice(slots)
        return (kind, idx), repository.pattern_candidates(pattern)


class CrosswordSolver:
    def __init__(self, size, repository, heuristic="mrv"):
        self.size = size
        self.repository = repository
        self.heuristic = heuristic
        self.heuristics = {
            "mrv": MinimumRemainingValuesHeuristic(),
            "random": RandomSlotHeuristic(),
        }

    def solve(self, puzzle):
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

        kind, idx = best
        random.shuffle(best_candidates)

        for word_idx in best_candidates:
            word = self.repository.words[word_idx]

            if puzzle.is_word_used(word):
                continue

            changed = puzzle.place(kind, idx, word)
            if changed is None:
                continue
            if self.solve(puzzle):
                return True
            puzzle.undo_place(kind, idx, changed)

        return False
