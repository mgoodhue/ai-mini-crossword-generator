import unittest

from crossword.dictionary import WordRepository
from crossword.grid import CrosswordGrid
from crossword.puzzle import Puzzle
from crossword.solver import CrosswordSolver


class WordRepositoryTests(unittest.TestCase):
    def test_pattern_candidates_filters_by_known_positions(self):
        repo = WordRepository(size=5, words=["apple", "angle", "amble", "alien"])
        matched_words = {repo.words[i] for i in repo.pattern_candidates("a..le")}
        self.assertEqual(matched_words, {"apple", "angle", "amble"})

    def test_pattern_candidates_returns_all_for_blank_pattern(self):
        repo = WordRepository(size=3, words=["cat", "dog", "eel"])
        indices = repo.pattern_candidates("...")
        self.assertEqual(set(indices), {0, 1, 2})


class CrosswordGridTests(unittest.TestCase):
    def test_place_and_undo_row(self):
        grid = CrosswordGrid(size=3)
        changed = grid.place_row(0, "cat")
        self.assertEqual(changed, [(0, 0), (0, 1), (0, 2)])
        self.assertEqual(grid.get_row_pattern(0), "cat")
        grid.undo(changed)
        self.assertEqual(grid.get_row_pattern(0), "...")

    def test_place_col_conflict_returns_none(self):
        grid = CrosswordGrid(size=3)
        grid.place_row(0, "cat")
        changed = grid.place_col(0, "dog")
        self.assertIsNone(changed)


class PuzzleTests(unittest.TestCase):
    def test_available_slots_reflects_placements(self):
        puzzle = Puzzle(CrosswordGrid(size=3))

        slots = puzzle.available_slots(3)
        self.assertEqual(len(slots), 6)

        changed = puzzle.place("row", 0, "cat")
        self.assertIsNotNone(changed)
        slots = puzzle.available_slots(3)

        row_slots = [slot for slot in slots if slot[0] == "row"]
        col_slots = [slot for slot in slots if slot[0] == "col"]
        self.assertEqual(len(row_slots), 2)
        self.assertEqual(len(col_slots), 3)

    def test_place_and_undo_place_restore_state(self):
        puzzle = Puzzle(CrosswordGrid(size=3))

        changed = puzzle.place("col", 1, "ace")
        self.assertIsNotNone(changed)
        self.assertEqual(puzzle.grid.get_col_pattern(1), "ace")
        self.assertEqual(puzzle.used_cols[1], "ace")

        puzzle.undo_place("col", 1, changed)
        self.assertEqual(puzzle.grid.get_col_pattern(1), "...")
        self.assertNotIn(1, puzzle.used_cols)

    def test_is_word_used_checks_rows_and_cols(self):
        puzzle = Puzzle(CrosswordGrid(size=3))
        self.assertFalse(puzzle.is_word_used("cat"))

        self.assertIsNotNone(puzzle.place("row", 0, "cat"))
        self.assertTrue(puzzle.is_word_used("cat"))
        self.assertFalse(puzzle.is_word_used("dog"))

    def test_is_complete_only_when_all_slots_filled(self):
        puzzle = Puzzle(CrosswordGrid(size=2))
        self.assertFalse(puzzle.is_complete(2))

        self.assertIsNotNone(puzzle.place("row", 0, "ab"))
        self.assertIsNotNone(puzzle.place("row", 1, "cd"))
        self.assertFalse(puzzle.is_complete(2))

        self.assertIsNotNone(puzzle.place("col", 0, "ac"))
        self.assertIsNotNone(puzzle.place("col", 1, "bd"))
        self.assertTrue(puzzle.is_complete(2))


class CrosswordSolverTests(unittest.TestCase):
    def test_solver_builds_consistent_grid_and_unique_words(self):
        words = [
            "ape",
            "man",
            "era",
            "ame",
            "par",
            "ena",
            "zzz",
        ]
        repo = WordRepository(size=3, words=words)
        puzzle = Puzzle(CrosswordGrid(size=3))
        solver = CrosswordSolver(size=3, repository=repo)

        solved = solver.solve(puzzle)

        self.assertTrue(solved)
        self.assertEqual(len(puzzle.used_rows), 3)
        self.assertEqual(len(puzzle.used_cols), 3)
        self.assertEqual(
            len(set(puzzle.used_rows.values()) & set(puzzle.used_cols.values())),
            0,
        )

        for row in range(3):
            self.assertEqual(puzzle.grid.get_row_pattern(row), puzzle.used_rows[row])
        for col in range(3):
            self.assertEqual(puzzle.grid.get_col_pattern(col), puzzle.used_cols[col])

    def test_solver_returns_false_when_unsatisfiable(self):
        repo = WordRepository(size=3, words=["cat", "dog", "eel"])
        puzzle = Puzzle(CrosswordGrid(size=3))
        solver = CrosswordSolver(size=3, repository=repo)

        solved = solver.solve(puzzle)

        self.assertFalse(solved)


if __name__ == "__main__":
    unittest.main()
