from .board import Board


SNAKE_WEIGHTS = [
    [2**15, 2**14, 2**13, 2**12],
    [2**8,  2**9,  2**10, 2**11],
    [2**7,  2**6,  2**5,  2**4],
    [2**0,  2**1,  2**2,  2**3],
]

def snake(board: Board) -> int:
    """Positional snake-pattern score only."""
    return sum(
        board.grid[r][c] * SNAKE_WEIGHTS[r][c]
        for r in range(4) for c in range(4)
    )


def empty_cells(board: Board) -> int:
    """Empty cell count only (scaled to be comparable with other heuristics)."""
    return len(board.get_empty_cells()) * 10000


def close_neighbors(board: Board) -> int:
    """Smoothness: penalise large differences between adjacent tiles."""
    grid = board.grid
    penalty = 0
    for r in range(4):
        for c in range(4):
            v = grid[r][c]
            if v == 0:
                continue
            if c + 1 < 4 and grid[r][c + 1]:
                penalty -= abs(v - grid[r][c + 1])
            if r + 1 < 4 and grid[r + 1][c]:
                penalty -= abs(v - grid[r + 1][c])
    return penalty


def combined(board: Board) -> int:
    """All three components together."""
    return snake(board) + empty_cells(board) + close_neighbors(board)


HEURISTICS = {
    'snake': snake,
    'empty': empty_cells,
    'smooth': close_neighbors,
    'combined': combined
}
