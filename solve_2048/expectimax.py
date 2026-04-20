from abc import ABC, abstractmethod

from .board import Board


class Node(ABC):

    def __init__(self, board: Board, last_move_score: int = 0):
        self.board = board
        self.last_move_score = last_move_score

    @abstractmethod
    def get_children(self) -> list[tuple['Node', float]]:
        pass


class MaxNode(Node):
    def get_children(self) -> list[tuple['Node', float]]:
        children = []
        for direction in ('left', 'right', 'up', 'down'):
            new_board, move_score = self.board.apply_move(direction)
            if new_board is not None:
                child = ChanceNode(new_board, move_score)
                children.append((child, 1.0))
        return children


class ChanceNode(Node):
    def get_children(self) -> list[tuple['Node', float]]:
        empty = self.board.get_empty_cells()
        if not empty:
            return []
        p_per_cell = 1.0 / len(empty)
        children = []
        for (r, c) in empty:
            for tile, tile_prob in ((2, 0.9), (4, 0.1)):
                new_board = self.board.copy()
                new_board.grid[r][c] = tile
                children.append((MaxNode(new_board, 0), p_per_cell * tile_prob))
        return children


def expectimax(node: Node, depth: int, heuristic) -> tuple[float, Node | None]:
    children = list(node.get_children())
    if depth == 0 or not children:
        return float(heuristic(node.board)), None

    if isinstance(node, MaxNode):
        best_score = float('-inf')
        best_child = None
        for child, prob in children:
            score, _ = expectimax(child, depth - 1, heuristic)
            if score > best_score:
                best_score, best_child = score, child
        return best_score, best_child

    expected = 0.0
    for child, prob in children:
        score, _ = expectimax(child, depth - 1, heuristic)
        expected += prob * score
    return expected, None
