import tkinter as tk
from tkinter import messagebox
import time
import copy


# ─────────────────────────────────────────────
#  DATASET  (12 puzzles: 4 per difficulty)
#  0 means the cell is empty
# ─────────────────────────────────────────────

PUZZLES = {
    "Easy": [
        # Puzzle 1
        [
            [5,3,0, 0,7,0, 0,0,0],
            [6,0,0, 1,9,5, 0,0,0],
            [0,9,8, 0,0,0, 0,6,0],

            [8,0,0, 0,6,0, 0,0,3],
            [4,0,0, 8,0,3, 0,0,1],
            [7,0,0, 0,2,0, 0,0,6],

            [0,6,0, 0,0,0, 2,8,0],
            [0,0,0, 4,1,9, 0,0,5],
            [0,0,0, 0,8,0, 0,7,9],
        ],
        # Puzzle 2
        [
            [0,0,3, 0,2,0, 6,0,0],
            [9,0,0, 3,0,5, 0,0,1],
            [0,0,1, 8,0,6, 4,0,0],

            [0,0,8, 1,0,2, 9,0,0],
            [7,0,0, 0,0,0, 0,0,8],
            [0,0,6, 7,0,8, 2,0,0],

            [0,0,2, 6,0,9, 5,0,0],
            [8,0,0, 2,0,3, 0,0,9],
            [0,0,5, 0,1,0, 3,0,0],
        ],
        # Puzzle 3
        [
            [2,0,0, 3,0,0, 0,0,0],
            [8,0,4, 0,6,2, 0,0,3],
            [0,1,3, 8,0,0, 2,0,0],

            [0,0,0, 0,2,0, 3,9,0],
            [5,0,7, 0,0,0, 6,2,1],
            [0,3,2, 0,0,6, 0,0,0],

            [0,2,0, 0,0,9, 1,4,0],
            [6,0,1, 2,5,0, 8,0,9],
            [0,0,0, 0,0,1, 0,0,2],
        ],
        # Puzzle 4
        [
            [0,0,0, 2,6,0, 7,0,1],
            [6,8,0, 0,7,0, 0,9,0],
            [1,9,0, 0,0,4, 5,0,0],

            [8,2,0, 1,0,0, 0,4,0],
            [0,0,4, 6,0,2, 9,0,0],
            [0,5,0, 0,0,3, 0,2,8],

            [0,0,9, 3,0,0, 0,7,4],
            [0,4,0, 0,5,0, 0,3,6],
            [7,0,3, 0,1,8, 0,0,0],
        ],
    ],

    "Medium": [
        # Puzzle 1
        [
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,3, 0,8,5],
            [0,0,1, 0,2,0, 0,0,0],

            [0,0,0, 5,0,7, 0,0,0],
            [0,0,4, 0,0,0, 1,0,0],
            [0,9,0, 0,0,0, 0,0,0],

            [5,0,0, 0,0,0, 0,7,3],
            [0,0,2, 0,1,0, 0,0,0],
            [0,0,0, 0,4,0, 0,0,9],
        ],
        # Puzzle 2
        [
            [0,0,5, 3,0,0, 0,0,0],
            [8,0,0, 0,0,0, 0,2,0],
            [0,7,0, 0,1,0, 5,0,0],

            [4,0,0, 0,0,5, 3,0,0],
            [0,1,0, 0,7,0, 0,0,6],
            [0,0,3, 2,0,0, 0,8,0],

            [0,6,0, 5,0,0, 0,0,9],
            [0,0,4, 0,0,0, 0,3,0],
            [0,0,0, 0,0,9, 7,0,0],
        ],
        # Puzzle 3
        [
            [1,0,0, 4,8,9, 0,0,6],
            [7,3,0, 0,0,0, 0,4,0],
            [0,0,0, 0,0,1, 2,9,5],

            [0,0,7, 1,2,0, 6,0,0],
            [5,0,0, 7,0,3, 0,0,8],
            [0,0,6, 0,9,5, 7,0,0],

            [9,1,4, 6,0,0, 0,0,0],
            [0,2,0, 0,0,0, 0,3,7],
            [8,0,0, 5,1,2, 0,0,4],
        ],
        # Puzzle 4
        [
            [0,2,0, 6,0,8, 0,0,0],
            [5,8,0, 0,0,9, 7,0,0],
            [0,0,0, 0,4,0, 0,0,0],

            [3,7,0, 0,0,0, 5,0,0],
            [6,0,0, 0,0,0, 0,0,4],
            [0,0,8, 0,0,0, 0,1,3],

            [0,0,0, 0,2,0, 0,0,0],
            [0,0,9, 8,0,0, 0,3,6],
            [0,0,0, 3,0,6, 0,9,0],
        ],
    ],

    "Hard": [
        # Puzzle 1
        [
            [8,0,0, 0,0,0, 0,0,0],
            [0,0,3, 6,0,0, 0,0,0],
            [0,7,0, 0,9,0, 2,0,0],

            [0,5,0, 0,0,7, 0,0,0],
            [0,0,0, 0,4,5, 7,0,0],
            [0,0,0, 1,0,0, 0,3,0],

            [0,0,1, 0,0,0, 0,6,8],
            [0,0,8, 5,0,0, 0,1,0],
            [0,9,0, 0,0,0, 4,0,0],
        ],
        # Puzzle 2
        [
            [0,0,0, 7,0,0, 0,0,0],
            [1,0,0, 0,0,0, 0,0,0],
            [0,0,0, 4,3,0, 2,0,0],

            [0,0,0, 0,0,0, 0,0,6],
            [0,0,0, 5,0,9, 0,0,0],
            [0,0,0, 0,0,0, 4,1,8],

            [0,0,0, 0,8,1, 0,0,0],
            [0,0,2, 0,0,0, 0,5,0],
            [0,4,0, 0,0,0, 3,0,0],
        ],
        # Puzzle 3
        [
            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,3, 0,8,5],
            [0,0,1, 0,2,0, 0,0,0],

            [0,0,0, 5,0,7, 0,0,0],
            [0,0,4, 0,0,0, 1,0,0],
            [0,9,0, 0,0,0, 0,0,0],

            [5,0,0, 0,0,0, 0,7,3],
            [0,0,2, 0,1,0, 0,0,0],
            [0,0,0, 0,4,0, 0,0,9],
        ],
        # Puzzle 4
        [
            [1,0,0, 0,0,7, 0,9,0],
            [0,3,0, 0,2,0, 0,0,8],
            [0,0,9, 6,0,0, 5,0,0],

            [0,0,5, 3,0,0, 9,0,0],
            [0,1,0, 0,8,0, 0,0,2],
            [6,0,0, 0,0,4, 0,0,0],

            [3,0,0, 0,0,0, 0,1,0],
            [0,4,0, 0,0,0, 0,0,7],
            [0,0,7, 0,0,0, 3,0,0],
        ],
    ],
}


# ─────────────────────────────────────────────
#  HELPER  –  basic Sudoku utility functions
# ─────────────────────────────────────────────

def get_peers(row, col):
    """Return all (r,c) positions that share a row, column, or 3x3 box with (row, col)."""
    peers = set()

    # same row
    for c in range(9):
        if c != col:
            peers.add((row, c))

    # same column
    for r in range(9):
        if r != row:
            peers.add((r, col))

    # same 3x3 box
    box_r = (row // 3) * 3
    box_c = (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if (r, c) != (row, col):
                peers.add((r, c))

    return peers


def board_to_domains(board):
    """
    Convert a 9x9 board (0 = empty) into a domains dict.
    Fixed cells get a single-value domain {val}.
    Empty cells start with domain {1..9}.
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = {board[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains


def domains_to_board(domains):
    """Turn a solved domains dict back into a 9x9 list of lists."""
    board = [[0]*9 for _ in range(9)]
    for (r, c), vals in domains.items():
        if len(vals) == 1:
            board[r][c] = next(iter(vals))
    return board


def is_valid_value(board, row, col, val):
    """Check if placing val at (row,col) breaks any Sudoku rule."""
    # check row
    if val in board[row]:
        return False

    # check column
    for r in range(9):
        if board[r][col] == val:
            return False

    # check 3x3 box
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == val:
                return False

    return True


# ─────────────────────────────────────────────
#  AC-3  ALGORITHM
# ─────────────────────────────────────────────

def revise(domains, xi, xj):
    """
    Remove values from domain[xi] that have no valid match in domain[xj].
    Returns True if the domain of xi was changed.
    """
    revised = False
    for x in set(domains[xi]):        # copy so we can remove while iterating
        # if no value y in xj's domain satisfies xi != xj, remove x
        if not any(x != y for y in domains[xj]):
            domains[xi].remove(x)
            revised = True
    return revised


def ac3(domains):
    """
    Run AC-3 on the Sudoku domains.
    Returns False if an inconsistency is found (empty domain), True otherwise.
    """
    # start with every arc (Xi, Xj) where Xi and Xj are peers
    queue = []
    for r in range(9):
        for c in range(9):
            for peer in get_peers(r, c):
                queue.append(((r, c), peer))

    while queue:
        xi, xj = queue.pop(0)

        if revise(domains, xi, xj):
            # if xi's domain is now empty, puzzle is unsolvable
            if len(domains[xi]) == 0:
                return False

            # neighbours of xi (except xj) may need re-checking
            for peer in get_peers(xi[0], xi[1]):
                if peer != xj:
                    queue.append((peer, xi))

    return True


def solve_ac3(board):
    """Solve a board using AC-3 alone. Returns solved board or None."""
    domains = board_to_domains(board)

    if not ac3(domains):
        return None

    # AC-3 might fully solve easy puzzles; check if every cell has exactly 1 value
    if all(len(v) == 1 for v in domains.values()):
        return domains_to_board(domains)

    # For harder puzzles AC-3 reduces domains but may not finish – fallback to backtracking
    return backtrack_with_domains(domains)


# ─────────────────────────────────────────────
#  BACKTRACKING  ALGORITHM
# ─────────────────────────────────────────────

def find_empty(board):
    """Find the next empty cell (value == 0). Returns (row, col) or None."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None


def solve_backtracking(board):
    """
    Solve using plain backtracking.
    Modifies board in-place and returns True when solved, False if no solution.
    """
    cell = find_empty(board)
    if cell is None:
        return True   # no empty cells left – solved!

    row, col = cell

    for val in range(1, 10):
        if is_valid_value(board, row, col, val):
            board[row][col] = val

            if solve_backtracking(board):
                return True

            # didn't work out – undo and try next value
            board[row][col] = 0

    return False   # trigger backtrack


def backtrack_with_domains(domains):
    """
    Backtracking that works on domains (used as AC-3 fallback).
    Returns a solved board or None.
    """
    # pick an unassigned cell (domain size > 1)
    unassigned = [(r, c) for (r, c), v in domains.items() if len(v) > 1]
    if not unassigned:
        return domains_to_board(domains)

    # pick cell with smallest remaining domain (MRV heuristic)
    r, c = min(unassigned, key=lambda cell: len(domains[cell]))

    for val in list(domains[(r, c)]):
        new_domains = copy.deepcopy(domains)
        new_domains[(r, c)] = {val}

        if ac3(new_domains):
            result = backtrack_with_domains(new_domains)
            if result is not None:
                return result

    return None


# ─────────────────────────────────────────────
#  GUI  –  built with Tkinter
# ─────────────────────────────────────────────

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver – Module 2")
        self.root.resizable(False, False)

        # current puzzle state
        self.current_board = None   # original puzzle
        self.solution = None        # fully solved board

        # cell entry widgets (9x9 grid)
        self.cells = [[None]*9 for _ in range(9)]

        self._build_ui()

    def _build_ui(self):
        """Create all widgets."""

        # ── top controls ──
        ctrl = tk.Frame(self.root, pady=6)
        ctrl.pack()

        tk.Label(ctrl, text="Difficulty:").grid(row=0, column=0, padx=4)
        self.diff_var = tk.StringVar(value="Easy")
        diff_menu = tk.OptionMenu(ctrl, self.diff_var, "Easy", "Medium", "Hard",
                                  command=lambda _: self._refresh_puzzle_menu())
        diff_menu.grid(row=0, column=1, padx=4)

        tk.Label(ctrl, text="Puzzle:").grid(row=0, column=2, padx=4)
        self.puzzle_var = tk.StringVar(value="1")
        self.puzzle_menu = tk.OptionMenu(ctrl, self.puzzle_var, "1", "2", "3", "4")
        self.puzzle_menu.grid(row=0, column=3, padx=4)

        tk.Button(ctrl, text="Load Puzzle", command=self._load_puzzle,
                  bg="#4a90d9", fg="white", width=10).grid(row=0, column=4, padx=8)

        # ── 9x9 grid ──
        grid_frame = tk.Frame(self.root, bg="black")
        grid_frame.pack(padx=10, pady=4)

        for r in range(9):
            for c in range(9):
                # thicker borders around 3x3 boxes
                pt = 3 if r % 3 == 0 else 1
                pl = 3 if c % 3 == 0 else 1
                pb = 3 if r == 8 else 1
                pr = 3 if c == 8 else 1

                frame = tk.Frame(grid_frame, bg="black",
                                 padx=pl, pady=pt)
                frame.grid(row=r, column=c,
                           padx=(pl, pr), pady=(pt, pb))

                e = tk.Entry(frame, width=2, font=("Arial", 18, "bold"),
                             justify="center", relief="flat", bg="white")
                e.pack()
                self.cells[r][c] = e

        # ── algorithm buttons ──
        algo_frame = tk.Frame(self.root, pady=6)
        algo_frame.pack()

        tk.Button(algo_frame, text="Solve with AC-3",
                  command=lambda: self._solve("AC-3"),
                  bg="#27ae60", fg="white", width=16).grid(row=0, column=0, padx=6)

        tk.Button(algo_frame, text="Solve with Backtracking",
                  command=lambda: self._solve("Backtracking"),
                  bg="#8e44ad", fg="white", width=20).grid(row=0, column=1, padx=6)

        tk.Button(algo_frame, text="Hint",
                  command=self._give_hint,
                  bg="#e67e22", fg="white", width=8).grid(row=0, column=2, padx=6)

        tk.Button(algo_frame, text="Reset",
                  command=self._reset_board,
                  bg="#c0392b", fg="white", width=8).grid(row=0, column=3, padx=6)

        # ── time display ──
        self.time_label = tk.Label(self.root, text="Time: –", font=("Arial", 11))
        self.time_label.pack(pady=4)

    def _refresh_puzzle_menu(self):
        """Update puzzle dropdown (always 1-4, just resets selection)."""
        self.puzzle_var.set("1")

    def _load_puzzle(self):
        """Load the selected puzzle into the grid."""
        diff = self.diff_var.get()
        idx = int(self.puzzle_var.get()) - 1

        self.current_board = copy.deepcopy(PUZZLES[diff][idx])
        self.solution = None   # clear old solution
        self.time_label.config(text="Time: –")

        self._draw_board(self.current_board, fixed_only=True)

    def _draw_board(self, board, fixed_only=False):
        """Fill the grid cells from a board. fixed_only = show only pre-filled values."""
        original = self.current_board

        for r in range(9):
            for c in range(9):
                entry = self.cells[r][c]
                entry.config(state="normal")
                entry.delete(0, tk.END)

                val = board[r][c]
                is_fixed = (original is not None and original[r][c] != 0)

                if val != 0:
                    if fixed_only and not is_fixed:
                        entry.config(bg="white", fg="black")
                    else:
                        entry.insert(0, str(val))
                        if is_fixed:
                            entry.config(bg="#dce8f7", fg="#1a1a1a", state="disabled")
                        else:
                            entry.config(bg="#e8f7dc", fg="#2d6a2d")

    def _solve(self, method):
        """Solve the current puzzle and show the result + time taken."""
        if self.current_board is None:
            messagebox.showwarning("No puzzle", "Please load a puzzle first.")
            return

        board_copy = copy.deepcopy(self.current_board)

        start = time.perf_counter()

        if method == "AC-3":
            solved = solve_ac3(board_copy)
        else:
            success = solve_backtracking(board_copy)
            solved = board_copy if success else None

        elapsed = time.perf_counter() - start

        if solved is None:
            messagebox.showerror("Error", "Puzzle could not be solved.")
            return

        self.solution = solved
        self._draw_board(solved)
        self.time_label.config(text=f"Time ({method}): {elapsed*1000:.3f} ms")

    def _give_hint(self):
        """Reveal the correct value for one empty cell."""
        if self.current_board is None:
            messagebox.showwarning("No puzzle", "Please load a puzzle first.")
            return

        # make sure we have a solution cached
        if self.solution is None:
            board_copy = copy.deepcopy(self.current_board)
            solved = solve_ac3(board_copy)
            if solved is None:
                messagebox.showerror("Error", "Cannot compute hint – puzzle unsolvable.")
                return
            self.solution = solved

        # find first cell that is empty in the current view
        for r in range(9):
            for c in range(9):
                entry = self.cells[r][c]
                if entry["state"] != "disabled" and entry.get() == "":
                    correct_val = self.solution[r][c]
                    entry.insert(0, str(correct_val))
                    entry.config(bg="#fff3cd", fg="#856404")   # yellow highlight
                    return

        messagebox.showinfo("Hint", "No empty cells found!")

    def _reset_board(self):
        """Clear user-entered values and go back to original puzzle."""
        if self.current_board is None:
            return
        self.solution = None
        self.time_label.config(text="Time: –")
        self._draw_board(self.current_board, fixed_only=True)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
