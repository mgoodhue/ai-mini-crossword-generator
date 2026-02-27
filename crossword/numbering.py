def _is_start_of_across(grid: list[str], row: int, col: int) -> bool:
    if grid[row][col] == "#":
        return False
    size = len(grid)
    if col > 0 and grid[row][col - 1] != "#":
        return False
    return col + 1 < size and grid[row][col + 1] != "#"


def _is_start_of_down(grid: list[str], row: int, col: int) -> bool:
    if grid[row][col] == "#":
        return False
    size = len(grid)
    if row > 0 and grid[row - 1][col] != "#":
        return False
    return row + 1 < size and grid[row + 1][col] != "#"


def build_clue_number_sequences(grid: list[str]) -> tuple[list[int], list[int]]:
    across_numbers: list[int] = []
    down_numbers: list[int] = []
    size = len(grid)
    clue_number = 1
    for row in range(size):
        for col in range(size):
            starts_across = _is_start_of_across(grid, row, col)
            starts_down = _is_start_of_down(grid, row, col)
            if not starts_across and not starts_down:
                continue
            if starts_across:
                across_numbers.append(clue_number)
            if starts_down:
                down_numbers.append(clue_number)
            clue_number += 1
    return across_numbers, down_numbers
