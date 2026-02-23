from dataclasses import dataclass

from .dictionary import WordRepository
from .grid import CrosswordGrid
from .puzzle import Puzzle
from .solver import CrosswordSolver


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
        repository = WordRepository.from_file(self.words_path, self.size)
        if self.difficulty not in {"easy", "standard", "hard"}:
            raise ValueError(
                f"Unknown difficulty '{self.difficulty}'. "
                "Expected one of: easy, standard, hard."
            )

        attempt_order: list[str] = [self.difficulty]
        if self.difficulty == "easy":
            attempt_order.append("standard")

        for level in attempt_order:
            puzzle = Puzzle(CrosswordGrid(self.size))
            solver = CrosswordSolver(self.size, repository, difficulty=level)
            solved = solver.solve(puzzle)

            if solved:
                across = [puzzle.used_rows[row].upper() for row in range(self.size)]
                down = [puzzle.used_cols[col].upper() for col in range(self.size)]
                grid_lines = [line.upper() for line in puzzle.grid.to_lines()]
                return GenerationResult(grid_lines=grid_lines, across=across, down=down)

        return None
