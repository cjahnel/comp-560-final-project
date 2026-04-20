"""Rudimentary visualization for the 2048 solver.

Usage: python main.py

Opens a small Tkinter window showing the 4x4 board, a list of immediate child states,
and controls to step/auto-play/reset. Uses `solve_2048` package modules.
"""
import tkinter as tk
from tkinter import ttk
import threading
import time

from solve_2048.board import Board
from solve_2048.heuristics import HEURISTICS
from solve_2048.expectimax import MaxNode, expectimax


class SolverUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('2048 Solver')
        self.resizable(False, False)

        self.board = Board()
        self.board.add_random_tile()
        self.board.add_random_tile()
        self.heuristic = HEURISTICS['combined']
        self.depth = 2
        self.running = False

        self._build_ui()
        self.update_board_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=8)
        frame.grid(row=0, column=0)

        # Board grid
        self.cells = []
        board_frame = ttk.Frame(frame)
        board_frame.grid(row=0, column=0, rowspan=4)
        # Create colored tile labels (use tk.Label so we can set bg/fg)
        for r in range(4):
            row = []
            for c in range(4):
                lbl = tk.Label(board_frame, text='', anchor='center', relief='ridge', bd=2)
                lbl.grid(row=r, column=c, padx=6, pady=6, sticky='nsew')
                row.append(lbl)
            self.cells.append(row)
        # Fix tile sizing by setting uniform min size for grid cells
        for r in range(4):
            board_frame.grid_rowconfigure(r, minsize=80)
        for c in range(4):
            board_frame.grid_columnconfigure(c, minsize=80)

        # Controls
        ttk.Label(frame, text='Depth:').grid(row=0, column=1, sticky='w')
        self.depth_var = tk.IntVar(value=self.depth)
        depth_spin = ttk.Spinbox(frame, from_=1, to=4, textvariable=self.depth_var, width=4)
        depth_spin.grid(row=0, column=2, sticky='w')

        # Speed slider (linear moves per second). Range 1..60
        ttk.Label(frame, text='Speed (moves/s):').grid(row=1, column=1, sticky='w')
        self.speed_var = tk.DoubleVar(value=5.0)
        # show moves/sec next to slider
        self.mps_var = tk.StringVar(value='')
        speed_scale = ttk.Scale(frame, from_=1.0, to=60.0, variable=self.speed_var, orient='horizontal', command=self.on_speed_change, length=160)
        speed_scale.grid(row=1, column=2, sticky='we')
        ttk.Label(frame, textvariable=self.mps_var).grid(row=1, column=3, sticky='w', padx=(6,0))
        # initialize display
        self.on_speed_change(self.speed_var.get())

        self.auto_btn = ttk.Button(frame, text='Auto Play', command=self.toggle_auto)
        self.auto_btn.grid(row=2, column=1, columnspan=2, sticky='we')

        ttk.Button(frame, text='Step', command=self.step).grid(row=3, column=1, columnspan=2, sticky='we')
        ttk.Button(frame, text='Reset', command=self.reset).grid(row=4, column=1, columnspan=2, sticky='we')

        # Child list
        ttk.Label(frame, text='Immediate children (move, score):').grid(row=5, column=0, columnspan=3, sticky='w', pady=(8, 0))
        # Use monospace font so columns align
        self.child_list = tk.Listbox(frame, width=40, height=8, font=('Courier', 10))
        self.child_list.grid(row=6, column=0, columnspan=3)

    def update_board_ui(self):
        for r in range(4):
            for c in range(4):
                v = self.board.grid[r][c]
                bg, fg = self.tile_colors().get(v, ('#3c3a32', '#f9f6f2'))
                txt = str(v) if v != 0 else ''
                # Adjust font size based on number of digits; keep 3-digit tiles same size as 2-digit
                digits = len(str(v)) if v != 0 else 0
                if digits <= 3:
                    fsize = 24
                elif digits == 4:
                    fsize = 18
                else:
                    fsize = 14
                self.cells[r][c].config(text=txt, bg=bg, fg=fg, font=('Helvetica', fsize, 'bold'))
        self.update_children()

    def tile_colors(self):
        # map tile value -> (bg, fg)
        return {
            0: ('#cdc1b4', '#776e65'),
            2: ('#eee4da', '#776e65'),
            4: ('#ede0c8', '#776e65'),
            8: ('#f2b179', '#f9f6f2'),
            16: ('#f59563', '#f9f6f2'),
            32: ('#f67c5f', '#f9f6f2'),
            64: ('#f65e3b', '#f9f6f2'),
            128: ('#edcf72', '#f9f6f2'),
            256: ('#edcc61', '#f9f6f2'),
            512: ('#edc850', '#f9f6f2'),
            1024: ('#edc53f', '#f9f6f2'),
            2048: ('#edc22e', '#f9f6f2'),
        }

    def on_speed_change(self, val):
        try:
            mps = float(val)
            self.mps_var.set(f"Moves/s: {mps:.2f}")
        except Exception:
            pass

    def update_children(self):
        self.child_list.delete(0, tk.END)
        node = MaxNode(self.board)
        children = []
        # compute expectimax values for each immediate child and get chosen move
        depth = int(self.depth_var.get())
        best_score, best_child = expectimax(node, depth, self.heuristic)
        # evaluate each immediate child separately to display values
        for item in node.get_children():
            ch_node = item[0] if isinstance(item, tuple) else item
            # value for this child (lookahead decreased by one)
            if depth > 0:
                val, _ = expectimax(ch_node, depth - 1, self.heuristic)
            else:
                val = float(self.heuristic(ch_node.board))
            # recover the direction that produced this child by matching boards
            direction = None
            for d in ('left', 'right', 'up', 'down'):
                nb, mv = self.board.apply_move(d)
                if nb is not None and nb.grid == ch_node.board.grid and mv == ch_node.last_move_score:
                    direction = d
                    break
            mv = ch_node.last_move_score
            children.append((val, direction, mv, ch_node))
        # sort children by heuristic value (highest first)
        children.sort(key=lambda t: t[0], reverse=True)
        chosen_move = None
        if best_child is not None:
            for _, direction, mv, ch in children:
                if best_child.board.grid == ch.board.grid and best_child.last_move_score == ch.last_move_score:
                    chosen_move = direction
                    break
        # header
        header = f"{'Move':<6}  {'Score':>6}  {'Heur':>8}"
        self.child_list.insert(tk.END, header)
        self.child_list.insert(tk.END, '-' * len(header))
        for hval, direction, mv, _ch in children:
            mark = '*' if direction == chosen_move else ' '
            self.child_list.insert(tk.END, f"{mark}{direction:<5}  {mv:6d}  {hval:8.3f}")

    def step(self):
        depth = int(self.depth_var.get())
        score, child_node = expectimax(MaxNode(self.board), depth, self.heuristic)
        if child_node is None:
            self.running = False
            return
        self.board = child_node.board
        self.board.add_random_tile()
        self.update_board_ui()

    def auto_loop(self):
        while self.running and not self.board.is_game_over():
            self.step()
            # Sleep based on moves/sec (linear). If 0, pause briefly.
            mps = float(self.speed_var.get())
            if mps > 0:
                time.sleep(max(0.001, 1.0 / mps))
            else:
                time.sleep(0.1)
        self.running = False
        self.auto_btn.config(text='Auto Play')

    def toggle_auto(self):
        if not self.running:
            self.running = True
            self.auto_btn.config(text='Stop')
            t = threading.Thread(target=self.auto_loop, daemon=True)
            t.start()
        else:
            self.running = False
            self.auto_btn.config(text='Auto Play')

    def reset(self):
        self.running = False
        self.board = Board()
        self.board.add_random_tile()
        self.board.add_random_tile()
        self.update_board_ui()


def main():
    app = SolverUI()
    app.mainloop()


if __name__ == '__main__':
    main()
