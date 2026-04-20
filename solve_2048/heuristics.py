from .board import Board


SNAKE_WEIGHTS = [
    [2**15, 2**14, 2**13, 2**12],
    [2**8,  2**9,  2**10, 2**11],
    [2**7,  2**6,  2**5,  2**4],
    [2**0,  2**1,  2**2,  2**3],
]

_MAX_SNAKE    = 500_000_000
_WORST_SMOOTH = -2046 * 24

W_SNAKE  = 1.0
W_EMPTY  = 0.05
W_SMOOTH = 0.05

def snake_raw(board: Board) -> float:
    return sum(
        board.grid[r][c] * SNAKE_WEIGHTS[r][c]
        for r in range(4) for c in range(4)
    )

def snake(board: Board) -> float:
    return min(snake_raw(board) / _MAX_SNAKE, 1.0)


def smooth_raw(board: Board) -> float:
    penalty = 0
    for r in range(4):
        for c in range(4):
            v = board.grid[r][c]
            if v == 0:
                continue
            if c + 1 < 4 and board.grid[r][c + 1]:
                penalty -= abs(v - board.grid[r][c + 1])
            if r + 1 < 4 and board.grid[r + 1][c]:
                penalty -= abs(v - board.grid[r + 1][c])
    return penalty

def close_neighbors(board: Board) -> float:
    return smooth_raw(board) / abs(_WORST_SMOOTH)


def empty_cells(board: Board) -> float:
    return len(board.get_empty_cells()) / 16


def combined(board: Board) -> float:
    s = min(snake_raw(board) / _MAX_SNAKE, 1.0)
    e = len(board.get_empty_cells()) / 16
    c = smooth_raw(board) / abs(_WORST_SMOOTH)
    return W_SNAKE * s + W_EMPTY * e + W_SMOOTH * c

HEURISTICS = {
    'snake': snake,
    'empty': empty_cells,
    'smooth': close_neighbors,
    'combined': combined
}
