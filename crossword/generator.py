from dataclasses import dataclass

from .dictionary import WordRepository
from .grid import CrosswordGrid
from .puzzle import Puzzle
from .solver import CrosswordSolver
from .slot import SlotKind


@dataclass
class GenerationResult:
    grid_lines: list[str]
    across: list[str]
    down: list[str]


class CrosswordGenerator:
    def __init__(
        self, size: int = 5, words_path: str = "words.txt", difficulty: str = "easy"
    ) -> None:
        self.size: int = size
        self.words_path: str = words_path
        self.difficulty: str = difficulty

    def generate(self) -> GenerationResult | None:
        repository = WordRepository.from_file(
            self.words_path,
            min_len=3,
            max_len=self.size,
        )
        if self.difficulty not in {"easy", "standard", "hard"}:
            raise ValueError(
                f"Unknown difficulty '{self.difficulty}'. "
                "Expected one of: easy, standard, hard."
            )

        attempt_order: list[str] = [self.difficulty]
        if self.difficulty == "easy":
            attempt_order.append("standard")

        block_layouts = self._block_layouts_for_size(self.size)
        attempts_per_layout = 20 if self.size >= 6 else 8

        for level in attempt_order:
            for blocks in block_layouts:
                for _ in range(attempts_per_layout):
                    puzzle = Puzzle(CrosswordGrid(self.size, blocks=blocks))
                    solver = CrosswordSolver(self.size, repository, difficulty=level)
                    solved = solver.solve(puzzle)

                    if solved:
                        across_words = puzzle.words_by_kind(SlotKind.ROW)
                        down_words = puzzle.words_by_kind(SlotKind.COL)
                        if not self._is_acceptable_fill(
                            puzzle,
                            across_words,
                            down_words,
                            blocks,
                        ):
                            continue

                        across = [word.upper() for word in across_words]
                        down = [word.upper() for word in down_words]
                        grid_lines = [line.upper() for line in puzzle.grid.to_lines()]
                        return GenerationResult(
                            grid_lines=grid_lines,
                            across=across,
                            down=down,
                        )

        return None

    def _block_layouts_for_size(self, size: int) -> list[set[tuple[int, int]]]:
        # Fallback to no blocks for tiny sizes where valid blocked layouts are too tight.
        if size < 5:
            return [set()]

        presets: dict[int, list[set[tuple[int, int]]]] = {
            5: [
                {
                    (0, 0),
                    (0, 4),
                    (4, 0),
                    (4, 4),
                }
            ],
            6: [
                {
                    (0, 1),
                    (0, 2),
                    (1, 1),
                    (1, 2),
                    (2, 1),
                    (3, 4),
                    (4, 3),
                    (4, 4),
                    (5, 3),
                    (5, 4),
                }
            ],
            7: [
                {
                    (0, 3),
                    (1, 3),
                    (2, 1),
                    (3, 0),
                    (3, 2),
                    (3, 4),
                    (3, 6),
                    (4, 5),
                    (5, 3),
                    (6, 3),
                }
            ],
            8: [
                {
                    (0, 3),
                    (1, 5),
                    (1, 6),
                    (1, 7),
                    (2, 1),
                    (2, 4),
                    (2, 5),
                    (3, 2),
                    (3, 4),
                    (4, 3),
                    (4, 5),
                    (5, 2),
                    (5, 3),
                    (5, 6),
                    (6, 0),
                    (6, 1),
                    (6, 2),
                    (7, 4),
                }
            ],
            9: [
                {
                    (0, 1),
                    (0, 5),
                    (1, 4),
                    (2, 1),
                    (2, 3),
                    (2, 5),
                    (3, 0),
                    (3, 6),
                    (4, 2),
                    (4, 6),
                    (5, 2),
                    (5, 8),
                    (6, 3),
                    (6, 5),
                    (6, 7),
                    (7, 4),
                    (8, 3),
                    (8, 7),
                }
            ],
        }

        corners = {
            (0, 0),
            (0, size - 1),
            (size - 1, 0),
            (size - 1, size - 1),
        }
        return [*presets.get(size, []), corners, set()]

    def _is_acceptable_fill(
        self,
        puzzle: Puzzle,
        across_words: list[str],
        down_words: list[str],
        blocks: set[tuple[int, int]],
    ) -> bool:
        # Reject partial fills with uncovered white cells.
        if any("." in line for line in puzzle.grid.to_lines()):
            return False

        # Avoid degenerate blocked grids (e.g. many Across clues but only one Down clue).
        if blocks:
            if len(across_words) < 3 or len(down_words) < 3:
                return False
        return True
