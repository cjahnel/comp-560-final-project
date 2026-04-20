import random


class Board:

    def __init__(self, grid: list[list[int]] | None = None) -> None:
        if grid is None:
            self.grid = [[0] * 4 for _ in range(4)]
        else:
            # make a deep copy
            self.grid = [row[:] for row in grid]

    def copy(self) -> 'Board':
        return Board(self.grid)

    def get_empty_cells(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]

    def add_random_tile(self) -> None:
        empty = self.get_empty_cells()
        if not empty:
            return
        r, c = random.choice(empty)
        self.grid[r][c] = 2 if random.random() < 0.9 else 4

    @staticmethod
    def _slide_row_left(row: list[int]) -> tuple[list[int], int]:
        tiles = [t for t in row if t != 0]
        merged: list[int] = []
        score = 0
        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                val = tiles[i] * 2
                merged.append(val)
                score += val
                i += 2
            else:
                merged.append(tiles[i])
                i += 1
        merged += [0] * (4 - len(merged))
        return merged, score

    @staticmethod
    def _rotate_cw(grid: list[list[int]]) -> list[list[int]]:
        return [list(row) for row in zip(*grid[::-1])]

    def apply_move(self, direction) -> tuple['Board | None', int]:
        # rotate so that the requested direction becomes a left slide
        # rotate counter-clockwise for 'up' (3 cw rotations) and clockwise
        # for 'down' (1 cw rotation)
        rot = {'left': 0, 'down': 1, 'right': 2, 'up': 3}[direction]
        b = [row[:] for row in self.grid]
        for _ in range(rot):
            b = Board._rotate_cw(b)
        new_b, total_score = [], 0
        for row in b:
            new_row, s = Board._slide_row_left(row)
            new_b.append(new_row)
            total_score += s
        for _ in range((4 - rot) % 4):
            new_b = Board._rotate_cw(new_b)
        if new_b == self.grid:
            return None, 0
        return Board(new_b), total_score

    def is_game_over(self) -> bool:
        return all(self.apply_move(d)[0] is None for d in ('left', 'right', 'up', 'down'))
