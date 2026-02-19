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
    def __init__(self, size=5, words_path="words.txt"):
        self.size = size
        self.words_path = words_path

    def generate(self):
        repository = WordRepository.from_file(self.words_path, self.size)
        puzzle = Puzzle(CrosswordGrid(self.size))
        solver = CrosswordSolver(self.size, repository)

        solved = solver.solve(puzzle)

        if not solved:
            return None

        across = [puzzle.used_rows[row].upper() for row in range(self.size)]
        down = [puzzle.used_cols[col].upper() for col in range(self.size)]
        grid_lines = [line.upper() for line in puzzle.grid.to_lines()]
        return GenerationResult(grid_lines=grid_lines, across=across, down=down)
