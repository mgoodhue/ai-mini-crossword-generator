import unittest
from pathlib import Path

from crossword import CrosswordGenerator
from crossword.dictionary import WordRepository
from crossword.grid import CrosswordGrid
from crossword.numbering import build_clue_number_sequences
from crossword.puzzle import Puzzle
from crossword.slot import Slot, SlotKind
from crossword.solver import CrosswordSolver


class WordRepositoryTests(unittest.TestCase):
    def test_pattern_candidates_filters_by_known_positions(self) -> None:
        repo = WordRepository(words=["apple", "angle", "amble", "alien"])
        matched_words = set(repo.pattern_candidates("a..le"))
        self.assertEqual(matched_words, {"apple", "angle", "amble"})

    def test_pattern_candidates_returns_all_for_blank_pattern(self) -> None:
        repo = WordRepository(words=["cat", "dog", "eel"])
        words = repo.pattern_candidates("...")
        self.assertEqual(set(words), {"cat", "dog", "eel"})


class CrosswordGridTests(unittest.TestCase):
    def test_place_and_undo_row(self) -> None:
        grid = CrosswordGrid(size=3)
        changed = grid.place_row(0, "cat")
        self.assertEqual(changed, [(0, 0), (0, 1), (0, 2)])
        self.assertEqual(grid.get_row_pattern(0), "cat")
        if changed is None:
            self.fail("Expected row placement to succeed")
        grid.undo(changed)
        self.assertEqual(grid.get_row_pattern(0), "...")

    def test_place_col_conflict_returns_none(self) -> None:
        grid = CrosswordGrid(size=3)
        grid.place_row(0, "cat")
        changed = grid.place_col(0, "dog")
        self.assertIsNone(changed)

    def test_place_slot_respects_blocks(self) -> None:
        grid = CrosswordGrid(size=5, blocks={(0, 0), (0, 4)})
        slot = Slot(SlotKind.ROW, index=0, start=1, length=3, pattern="...")
        changed = grid.place_slot(slot, "cat")
        self.assertEqual(changed, [(0, 1), (0, 2), (0, 3)])
        self.assertEqual(grid.get_row_pattern(0), "#cat#")


class PuzzleTests(unittest.TestCase):
    def test_available_slots_reflects_placements(self) -> None:
        puzzle = Puzzle(CrosswordGrid(size=5, blocks={(0, 0), (0, 4), (4, 0), (4, 4)}))

        slots = puzzle.available_slots()
        self.assertEqual(len(slots), 10)

        changed = puzzle.place(Slot(SlotKind.ROW, index=0, start=1, length=3, pattern="..."), "cat")
        self.assertIsNotNone(changed)
        slots = puzzle.available_slots()

        row_slots = [slot for slot in slots if slot.kind == SlotKind.ROW]
        col_slots = [slot for slot in slots if slot.kind == SlotKind.COL]
        self.assertEqual(len(row_slots), 4)
        self.assertEqual(len(col_slots), 5)

    def test_place_and_undo_place_restore_state(self) -> None:
        puzzle = Puzzle(CrosswordGrid(size=3))

        changed = puzzle.place(
            Slot(SlotKind.COL, index=1, start=0, length=3, pattern="..."), "ace"
        )
        self.assertIsNotNone(changed)
        self.assertEqual(puzzle.grid.get_col_pattern(1), "ace")
        self.assertTrue(puzzle.is_word_used("ace"))
        if changed is None:
            self.fail("Expected column placement to succeed")

        puzzle.undo_place(
            Slot(SlotKind.COL, index=1, start=0, length=3, pattern="ace"), changed
        )
        self.assertEqual(puzzle.grid.get_col_pattern(1), "...")
        self.assertFalse(puzzle.is_word_used("ace"))

    def test_is_word_used_checks_rows_and_cols(self) -> None:
        puzzle = Puzzle(CrosswordGrid(size=3))
        self.assertFalse(puzzle.is_word_used("cat"))

        self.assertIsNotNone(
            puzzle.place(Slot(SlotKind.ROW, index=0, start=0, length=3, pattern="..."), "cat")
        )
        self.assertTrue(puzzle.is_word_used("cat"))
        self.assertFalse(puzzle.is_word_used("dog"))

    def test_is_complete_only_when_all_slots_filled(self) -> None:
        puzzle = Puzzle(CrosswordGrid(size=2), min_slot_length=2)
        self.assertFalse(puzzle.is_complete())

        self.assertIsNotNone(
            puzzle.place(Slot(SlotKind.ROW, index=0, start=0, length=2, pattern=".."), "ab")
        )
        self.assertIsNotNone(
            puzzle.place(Slot(SlotKind.ROW, index=1, start=0, length=2, pattern=".."), "cd")
        )
        self.assertFalse(puzzle.is_complete())

        self.assertIsNotNone(
            puzzle.place(Slot(SlotKind.COL, index=0, start=0, length=2, pattern=".."), "ac")
        )
        self.assertIsNotNone(
            puzzle.place(Slot(SlotKind.COL, index=1, start=0, length=2, pattern=".."), "bd")
        )
        self.assertTrue(puzzle.is_complete())


class CrosswordSolverTests(unittest.TestCase):
    def test_solver_builds_consistent_grid(self) -> None:
        words = [
            "ape",
            "man",
            "era",
            "ame",
            "par",
            "ena",
            "zzz",
        ]
        repo = WordRepository(words=words)
        puzzle = Puzzle(CrosswordGrid(size=3))
        solver = CrosswordSolver(size=3, repository=repo)

        solved = solver.solve(puzzle)

        self.assertTrue(solved)
        across = puzzle.words_by_kind(SlotKind.ROW)
        down = puzzle.words_by_kind(SlotKind.COL)
        self.assertEqual(len(across), 3)
        self.assertEqual(len(down), 3)
        for row in range(3):
            self.assertIn(puzzle.grid.get_row_pattern(row), across)
        for col in range(3):
            self.assertIn(puzzle.grid.get_col_pattern(col), down)

    def test_solver_returns_false_when_unsatisfiable(self) -> None:
        repo = WordRepository(words=["cat", "dog", "eel"])
        puzzle = Puzzle(CrosswordGrid(size=3))
        solver = CrosswordSolver(size=3, repository=repo)

        solved = solver.solve(puzzle)

        self.assertFalse(solved)


class GeneratorTests(unittest.TestCase):
    def test_generator_supports_sizes_three_through_nine(self) -> None:
        words_path = Path(__file__).resolve().parents[1] / "words.txt"
        for size in range(3, 10):
            result = CrosswordGenerator(
                size=size,
                words_path=str(words_path),
                difficulty="standard",
            ).generate()
            self.assertIsNotNone(result, f"Expected puzzle for size {size}")


class ClueNumberingTests(unittest.TestCase):
    def test_clue_numbers_are_shared_between_across_and_down_starts(self) -> None:
        grid = [
            ".#...",
            ".....",
            "..#..",
            ".....",
            "...#.",
        ]
        across, down = build_clue_number_sequences(grid)
        self.assertEqual(across, [2, 5, 7, 8, 9, 11])
        self.assertEqual(down, [1, 2, 3, 4, 6, 10])

    def test_single_open_cell_has_no_clue_number(self) -> None:
        grid = [
            "###",
            "#.#",
            "###",
        ]
        across, down = build_clue_number_sequences(grid)
        self.assertEqual(across, [])
        self.assertEqual(down, [])


if __name__ == "__main__":
    unittest.main()
