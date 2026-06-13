"""
#24F-0542_MuhammadHumd_Module-1_AI-LAB_Project
=============================================================
  MODULE 1 Intelligent Urban Delivery Robot
=============================================================
  Search Algorithms: BFS, DFS, UCS, Greedy Best-First, A*
  Grid: 15x15 | 5 Deliveries | Full Visualization
=============================================================
"""

import random
import heapq
import time
import math
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import threading

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
GRID_SIZE    = 15
CELL_PX      = 48          # pixels per cell
PADDING      = 10

EMPTY        = 0
BUILDING     = 1
TRAFFIC      = 2
DELIVERY     = 3
BASE         = 4

# Color palette
COLORS = {
    EMPTY:    "#1e293b",   # dark slate – road
    BUILDING: "#64748b",   # slate – obstacles
    TRAFFIC:  "#f59e0b",   # amber – traffic zone
    DELIVERY: "#10b981",   # emerald – delivery point
    BASE:     "#6366f1",   # indigo – base station
    "path":   "#38bdf8",   # sky blue – planned path
    "robot":  "#f43f5e",   # rose – robot
    "visited":"#0f172a",   # very dark – explored nodes
    "grid":   "#0f172a",   # grid line color
    "done":   "#4ade80",   # green – completed delivery
}

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]   # Up Down Left Right


# ─────────────────────────────────────────────────────────────
#  GRID / ENVIRONMENT
# ─────────────────────────────────────────────────────────────
class Grid:
    def __init__(self):
        self.cells     = [[EMPTY]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.costs     = [[0]*GRID_SIZE     for _ in range(GRID_SIZE)]
        self.base      = None
        self.deliveries= []
        self._generate()

    def _generate(self):
        random.seed(42)          # reproducible layout

        # ── Base station (fixed top-left area)
        self.base = (1, 1)
        self.cells[1][1] = BASE

        # ── Scatter buildings  (~20% of cells)
        for _ in range(45):
            r, c = random.randint(0,14), random.randint(0,14)
            if (r,c) != self.base:
                self.cells[r][c] = BUILDING

        # ── Traffic zones  (~10% of remaining road cells)
        for _ in range(22):
            r, c = random.randint(0,14), random.randint(0,14)
            if self.cells[r][c] == EMPTY:
                self.cells[r][c] = TRAFFIC

        # ── Assign traversal costs
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                ct = self.cells[r][c]
                if ct == BUILDING:
                    self.costs[r][c] = float('inf')
                elif ct == TRAFFIC:
                    self.costs[r][c] = random.randint(10, 20)
                else:
                    self.costs[r][c] = random.randint(1, 5)

        # ── Five delivery locations (reachable road cells)
        road_cells = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                      if self.cells[r][c] in (EMPTY, TRAFFIC) and (r,c)!=self.base]
        chosen = random.sample(road_cells, 5)
        for pos in chosen:
            self.deliveries.append(pos)
            self.cells[pos[0]][pos[1]] = DELIVERY
            self.costs[pos[0]][pos[1]] = random.randint(1, 5)

    def is_valid(self, r, c):
        return 0<=r<GRID_SIZE and 0<=c<GRID_SIZE and self.cells[r][c] != BUILDING

    def cost(self, r, c):
        return self.costs[r][c]

    def neighbors(self, r, c):
        for dr,dc in DIRECTIONS:
            nr,nc = r+dr, c+dc
            if self.is_valid(nr,nc):
                yield (nr,nc)


# ─────────────────────────────────────────────────────────────
#  HEURISTICS
# ─────────────────────────────────────────────────────────────
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def combined_heuristic(a, b):
    """Weighted combination – used by Greedy & A*"""
    return (manhattan(a,b) + euclidean(a,b)) / 2


# ─────────────────────────────────────────────────────────────
#  SEARCH ALGORITHMS
# ─────────────────────────────────────────────────────────────
def reconstruct(parent, start, goal):
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def bfs(grid, start, goal):
    """Breadth-First Search – ignores edge costs."""
    queue   = deque([start])
    parent  = {start: None}
    visited = set([start])
    nodes_explored = 0

    while queue:
        cur = queue.popleft()
        nodes_explored += 1
        if cur == goal:
            path = reconstruct(parent, start, goal)
            cost = sum(grid.cost(r,c) for r,c in path)
            return path, cost, nodes_explored, list(visited)
        for nb in grid.neighbors(*cur):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                queue.append(nb)
    return None, float('inf'), nodes_explored, list(visited)


def dfs(grid, start, goal):
    """Depth-First Search – ignores edge costs."""
    stack   = [start]
    parent  = {start: None}
    visited = set()
    nodes_explored = 0

    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        nodes_explored += 1
        if cur == goal:
            path = reconstruct(parent, start, goal)
            cost = sum(grid.cost(r,c) for r,c in path)
            return path, cost, nodes_explored, list(visited)
        for nb in grid.neighbors(*cur):
            if nb not in visited:
                parent[nb] = cur
                stack.append(nb)
    return None, float('inf'), nodes_explored, list(visited)


def ucs(grid, start, goal):
    """Uniform Cost Search – optimal with variable costs."""
    heap    = [(0, start)]
    cost_so = {start: 0}
    parent  = {start: None}
    visited = set()
    nodes_explored = 0

    while heap:
        g, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)
        nodes_explored += 1
        if cur == goal:
            path = reconstruct(parent, start, goal)
            return path, g, nodes_explored, list(visited)
        for nb in grid.neighbors(*cur):
            new_cost = g + grid.cost(*nb)
            if nb not in cost_so or new_cost < cost_so[nb]:
                cost_so[nb] = new_cost
                parent[nb]  = cur
                heapq.heappush(heap, (new_cost, nb))
    return None, float('inf'), nodes_explored, list(visited)


def greedy(grid, start, goal):
    """Greedy Best-First Search – uses heuristic only."""
    heap    = [(combined_heuristic(start,goal), start)]
    parent  = {start: None}
    visited = set()
    nodes_explored = 0

    while heap:
        _, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)
        nodes_explored += 1
        if cur == goal:
            path = reconstruct(parent, start, goal)
            cost = sum(grid.cost(r,c) for r,c in path)
            return path, cost, nodes_explored, list(visited)
        for nb in grid.neighbors(*cur):
            if nb not in visited:
                parent[nb] = cur
                heapq.heappush(heap, (combined_heuristic(nb,goal), nb))
    return None, float('inf'), nodes_explored, list(visited)


def astar(grid, start, goal):
    """A* Search – combines actual cost + heuristic."""
    heap    = [(combined_heuristic(start,goal), 0, start)]
    cost_so = {start: 0}
    parent  = {start: None}
    visited = set()
    nodes_explored = 0

    while heap:
        f, g, cur = heapq.heappop(heap)
        if cur in visited:
            continue
        visited.add(cur)
        nodes_explored += 1
        if cur == goal:
            path = reconstruct(parent, start, goal)
            return path, g, nodes_explored, list(visited)
        for nb in grid.neighbors(*cur):
            new_g = g + grid.cost(*nb)
            if nb not in cost_so or new_g < cost_so[nb]:
                cost_so[nb] = new_g
                parent[nb]  = cur
                h = combined_heuristic(nb,goal)
                heapq.heappush(heap, (new_g+h, new_g, nb))
    return None, float('inf'), nodes_explored, list(visited)


ALGORITHMS = {
    "BFS"   : bfs,
    "DFS"   : dfs,
    "UCS"   : ucs,
    "Greedy": greedy,
    "A*"    : astar,
}


# ─────────────────────────────────────────────────────────────
#  TKINTER GUI
# ─────────────────────────────────────────────────────────────
class RobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🤖 Intelligent Urban Delivery Robot – ")
        self.configure(bg="#0f172a")
        self.resizable(False, False)

        self.grid_env    = Grid()
        self.robot_pos   = self.grid_env.base
        self.algo_var    = tk.StringVar(value="A*")
        self.status_var  = tk.StringVar(value="Ready. Press  ▶ Run Delivery  to start.")
        self.delivery_idx= 0
        self.results     = []          # store metrics per delivery
        self.running     = False

        self._build_ui()
        self._draw_grid()

    # ── Layout ──────────────────────────────────────────────
    def _build_ui(self):
        W = GRID_SIZE * CELL_PX + PADDING*2
        H = GRID_SIZE * CELL_PX + PADDING*2

        # LEFT – canvas
        left = tk.Frame(self, bg="#0f172a")
        left.grid(row=0, column=0, padx=(16,8), pady=16)

        self.canvas = tk.Canvas(left, width=W, height=H,
                                bg="#0f172a", highlightthickness=0)
        self.canvas.pack()

        # RIGHT – controls + stats
        right = tk.Frame(self, bg="#0f172a", width=340)
        right.grid(row=0, column=1, sticky="ns", padx=(8,16), pady=16)
        right.grid_propagate(False)

        # Title
        tk.Label(right, text="🤖 Urban Delivery Robot",
                 font=("Courier New",16,"bold"),
                 bg="#0f172a", fg="#38bdf8").pack(pady=(0,4))
        

        # Algorithm selector
        tk.Label(right, text="Algorithm",
                 font=("Courier New",11,"bold"),
                 bg="#0f172a", fg="#94a3b8").pack(anchor="w")
        frm_algo = tk.Frame(right, bg="#0f172a")
        frm_algo.pack(fill="x", pady=(4,12))
        for alg in ALGORITHMS:
            rb = tk.Radiobutton(frm_algo, text=alg, variable=self.algo_var,
                                value=alg, font=("Courier New",10),
                                bg="#0f172a", fg="#e2e8f0",
                                selectcolor="#1e293b",
                                activebackground="#0f172a",
                                activeforeground="#38bdf8")
            rb.pack(anchor="w")

        # Buttons
        btn_cfg = dict(font=("Courier New",11,"bold"), relief="flat",
                       cursor="hand2", pady=8)
        self.btn_run = tk.Button(right, text="▶  Run Delivery",
                                 bg="#6366f1", fg="white",
                                 command=self._run_delivery, **btn_cfg)
        self.btn_run.pack(fill="x", pady=(0,6))

        self.btn_all = tk.Button(right, text="⚡  Run All 5 Deliveries",
                                 bg="#0ea5e9", fg="white",
                                 command=self._run_all, **btn_cfg)
        self.btn_all.pack(fill="x", pady=(0,6))

        self.btn_reset = tk.Button(right, text="↺  Reset",
                                   bg="#334155", fg="#e2e8f0",
                                   command=self._reset, **btn_cfg)
        self.btn_reset.pack(fill="x", pady=(0,16))

        # Status bar
        tk.Label(right, textvariable=self.status_var,
                 font=("Courier New",9), bg="#1e293b", fg="#7dd3fc",
                 wraplength=300, justify="left", padx=8, pady=6).pack(fill="x")

        # Separator
        tk.Frame(right, bg="#1e293b", height=2).pack(fill="x", pady=12)

        # Metrics table header
        tk.Label(right, text="📊 Delivery Metrics",
                 font=("Courier New",11,"bold"),
                 bg="#0f172a", fg="#94a3b8").pack(anchor="w", pady=(0,6))

        cols = ("Delivery","Algorithm","Cost","Time(ms)","Nodes")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=7)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1e293b", foreground="#e2e8f0",
                        fieldbackground="#1e293b", rowheight=22,
                        font=("Courier New",8))
        style.configure("Treeview.Heading",
                        background="#0f172a", foreground="#38bdf8",
                        font=("Courier New",8,"bold"))
        style.map("Treeview", background=[("selected","#334155")])

        widths = [60, 70, 50, 70, 60]
        for col,w in zip(cols,widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="x", pady=(0,8))

        # Legend
        tk.Label(right, text="Legend",
                 font=("Courier New",10,"bold"),
                 bg="#0f172a", fg="#94a3b8").pack(anchor="w", pady=(8,4))
        legend = [
            (COLORS[BASE],    "Base Station"),
            (COLORS[DELIVERY],"Delivery Point"),
            (COLORS[BUILDING],"Building / Obstacle"),
            (COLORS[TRAFFIC], "Traffic Zone"),
            (COLORS[EMPTY],   "Road"),
            (COLORS["path"],  "Planned Path"),
            (COLORS["robot"], "Robot"),
        ]
        for color, label in legend:
            row = tk.Frame(right, bg="#0f172a")
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=color, width=3, relief="solid").pack(side="left", padx=(0,6))
            tk.Label(row, text=label, font=("Courier New",8),
                     bg="#0f172a", fg="#cbd5e1").pack(side="left")

    # ── Drawing ─────────────────────────────────────────────
    def _cell_xy(self, r, c):
        x = PADDING + c * CELL_PX
        y = PADDING + r * CELL_PX
        return x, y

    def _draw_grid(self, path=None, visited=None):
        self.canvas.delete("all")
        g = self.grid_env

        visited_set = set(visited) if visited else set()
        path_set    = set(path)    if path    else set()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x, y = self._cell_xy(r, c)
                ct   = g.cells[r][c]

                if (r,c) in path_set:
                    fill = COLORS["path"]
                elif (r,c) in visited_set and ct not in (BUILDING,):
                    fill = "#164e63"   # teal-dark explored
                else:
                    fill = COLORS[ct]

                self.canvas.create_rectangle(x, y, x+CELL_PX, y+CELL_PX,
                                             fill=fill, outline=COLORS["grid"],
                                             width=1)

                # Cost label on road/traffic
                if ct in (EMPTY, TRAFFIC) and (r,c) != self.grid_env.base:
                    self.canvas.create_text(x+CELL_PX//2, y+CELL_PX//2,
                                            text=str(g.costs[r][c]),
                                            font=("Courier New",7),
                                            fill="#475569" if ct==EMPTY else "#78350f")

                # Delivery numbers
                if ct == DELIVERY:
                    idx = g.deliveries.index((r,c)) + 1 if (r,c) in g.deliveries else "?"
                    self.canvas.create_text(x+CELL_PX//2, y+CELL_PX//2,
                                            text=f"D{idx}", font=("Courier New",9,"bold"),
                                            fill="white")

        # Draw robot
        rx, ry = self._cell_xy(*self.robot_pos)
        self.canvas.create_oval(rx+6, ry+6, rx+CELL_PX-6, ry+CELL_PX-6,
                                fill=COLORS["robot"], outline="white", width=2)
        self.canvas.create_text(rx+CELL_PX//2, ry+CELL_PX//2,
                                text="🤖", font=("Courier New",12))

    def _animate_path(self, path):
        """Animate robot moving along path."""
        if not path:
            return
        for i, pos in enumerate(path):
            self.robot_pos = pos
            self._draw_grid(path=path[:i+1])
            self.update()
            time.sleep(0.12)

    # ── Actions ─────────────────────────────────────────────
    def _run_delivery(self):
        if self.running:
            return
        if self.delivery_idx >= len(self.grid_env.deliveries):
            messagebox.showinfo("Done", "All 5 deliveries completed! 🎉")
            return
        self.running = True
        self.btn_run.config(state="disabled")
        self.btn_all.config(state="disabled")
        threading.Thread(target=self._execute_delivery, daemon=True).start()

    def _run_all(self):
        if self.running:
            return
        self.running = True
        self.btn_run.config(state="disabled")
        self.btn_all.config(state="disabled")
        threading.Thread(target=self._execute_all, daemon=True).start()

    def _execute_all(self):
        while self.delivery_idx < len(self.grid_env.deliveries):
            self._execute_delivery(step_mode=False)
        self.running = False
        self.btn_run.config(state="normal")
        self.btn_all.config(state="normal")
        self._show_summary()

    def _execute_delivery(self, step_mode=True):
        idx  = self.delivery_idx
        goal = self.grid_env.deliveries[idx]
        algo_name = self.algo_var.get()
        algo_fn   = ALGORITHMS[algo_name]

        self.status_var.set(f"Delivery {idx+1}/5 → {goal}  [{algo_name}]  Computing path…")
        self.update()

        t0 = time.perf_counter()
        path, cost, nodes, visited = algo_fn(self.grid_env, self.robot_pos, goal)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if path is None:
            self.status_var.set(f"❌ No path found to {goal}! Skipping.")
            self.delivery_idx += 1
            self.running = False
            self.btn_run.config(state="normal")
            self.btn_all.config(state="normal")
            return

        # Show explored nodes briefly
        self._draw_grid(visited=visited)
        self.update()
        time.sleep(0.4)

        # Animate movement
        self._animate_path(path)

        # Mark delivery done
        self.grid_env.cells[goal[0]][goal[1]] = EMPTY   # delivered
        self.robot_pos = goal
        self.delivery_idx += 1

        # Record metrics
        record = {
            "delivery": idx+1,
            "algo"    : algo_name,
            "cost"    : cost,
            "time_ms" : elapsed_ms,
            "nodes"   : nodes,
            "path_len": len(path),
        }
        self.results.append(record)

        # Update table
        self.tree.insert("", "end", values=(
            f"#{idx+1}", algo_name,
            f"{cost:.1f}", f"{elapsed_ms:.2f}", nodes
        ))

        self.status_var.set(
            f"✅ Delivery {idx+1} done! Cost={cost:.1f}  "
            f"Nodes={nodes}  Time={elapsed_ms:.2f}ms"
        )
        self._draw_grid()
        self.update()

        if step_mode:
            self.running = False
            self.btn_run.config(state="normal")
            self.btn_all.config(state="normal")
            if self.delivery_idx >= 5:
                self._show_summary()

    def _reset(self):
        self.grid_env     = Grid()
        self.robot_pos    = self.grid_env.base
        self.delivery_idx = 0
        self.results      = []
        self.running      = False
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Reset complete. Choose algorithm and press ▶ Run Delivery.")
        self.btn_run.config(state="normal")
        self.btn_all.config(state="normal")
        self._draw_grid()

    def _show_summary(self):
        if not self.results:
            return
        lines = ["\n" + "="*50,
                 "  PERFORMANCE SUMMARY",
                 "="*50]
        for r in self.results:
            lines.append(
                f"  Delivery #{r['delivery']} | {r['algo']:6s} | "
                f"Cost={r['cost']:.1f} | Nodes={r['nodes']} | "
                f"Time={r['time_ms']:.2f}ms | Steps={r['path_len']}"
            )
        total_cost = sum(r['cost'] for r in self.results)
        lines += ["="*50,
                  f"  Total Path Cost : {total_cost:.1f}",
                  "="*50 + "\n"]
        print("\n".join(lines))
        messagebox.showinfo(
            "All Deliveries Complete! 🎉",
            f"All 5 deliveries completed!\n\nTotal path cost: {total_cost:.1f}\n\n"
            "Full performance table printed to console."
        )


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()