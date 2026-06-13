"""
=============================================================================
MODULE 3 - Automated Exam Management System using K-Means Clustering
=============================================================================
Description:
    This program implements an automated exam management system for
    National University (FAST) that uses K-Means clustering to group
    students by domain and batch, then generates an optimized seating
    plan and faculty allocation for exam rooms.

Features:
    - Synthetic student data generation for 5 domains across 5 batches
    - K-Means clustering for student grouping
    - Automated seating plan generation respecting room capacities
    - Faculty allocation based on domain expertise
    - Summary report generation
    - Interactive GUI for administrators

Author: AL-2002 Project 2026
Institution: National University FAST - Faisalabad Chiniot Campus
=============================================================================
"""

# ─── Standard & Third-Party Imports ─────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import random
import warnings
warnings.filterwarnings("ignore")


# ─── Global Constants ────────────────────────────────────────────────────────

DOMAINS = [
    "Computer Science",
    "Artificial Intelligence",
    "Business Analytics",
    "Software Engineering",
    "Electrical Engineering",
]

BATCHES = [19, 20, 21, 22, 23]

# Approximate students per domain per batch
STUDENTS_PER_DOMAIN_BATCH = {
    "Computer Science":       {19: 110, 20: 120, 21: 115, 22: 105, 23: 100},
    "Artificial Intelligence":{19:  90, 20:  95, 21: 100, 22:  95, 23:  90},
    "Business Analytics":     {19:  80, 20:  85, 21:  90, 22:  85, 23:  80},
    "Software Engineering":   {19: 100, 20: 105, 21: 110, 22: 100, 23:  95},
    "Electrical Engineering": {19:  95, 20:  90, 21:  95, 22:  90, 23:  85},
}

# 30 rooms: most 30-35 seats, a few 25 seats
ROOM_CAPACITIES = (
    [25] * 5          # 5 small rooms
    + [30] * 12       # 12 medium rooms
    + [35] * 13       # 13 large rooms
)
ROOM_NAMES = [f"Room-{i+1:02d}" for i in range(30)]

# Faculty list per domain (3 per domain)
FACULTY_POOL = {
    domain: [f"Prof. {domain.split()[0][0]}{i+1}" for i in range(3)]
    for domain in DOMAINS
}


# ─── Data Generation ─────────────────────────────────────────────────────────

def generate_student_data() -> pd.DataFrame:
    """
    Generate synthetic student records for all domains and batches.

    Returns:
        pd.DataFrame: One row per student with columns
                      [student_id, name, batch, domain, roll_no].
    """
    records = []
    student_id = 1

    for domain in DOMAINS:
        for batch in BATCHES:
            count = STUDENTS_PER_DOMAIN_BATCH[domain][batch]
            for i in range(count):
                roll = f"{batch}F{student_id:04d}"
                records.append({
                    "student_id": student_id,
                    "roll_no":    roll,
                    "name":       f"Student_{student_id}",
                    "batch":      batch,
                    "domain":     domain,
                })
                student_id += 1

    df = pd.DataFrame(records)
    return df


def generate_faculty_data() -> pd.DataFrame:
    """
    Generate faculty records with domain expertise.

    Returns:
        pd.DataFrame: Columns [faculty_id, name, domain].
    """
    records = []
    fid = 1
    for domain, names in FACULTY_POOL.items():
        for name in names:
            records.append({"faculty_id": fid, "name": name, "domain": domain})
            fid += 1
    return pd.DataFrame(records)


# ─── Data Preprocessing ──────────────────────────────────────────────────────

def preprocess_data(student_df: pd.DataFrame):
    """
    Encode categorical features and scale numerical ones so they are
    suitable for K-Means clustering.

    Args:
        student_df: Raw student DataFrame.

    Returns:
        tuple: (features_scaled, domain_encoded, batch_normalized, scaler)
    """
    # Encode domain as integer
    domain_map  = {d: i for i, d in enumerate(DOMAINS)}
    batch_min, batch_max = min(BATCHES), max(BATCHES)

    domain_enc = student_df["domain"].map(domain_map).values.astype(float)
    batch_norm = (student_df["batch"].values - batch_min) / (batch_max - batch_min)

    features = np.column_stack([domain_enc, batch_norm])
    scaler   = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    return features_scaled, domain_enc, batch_norm, scaler


# ─── K-Means Clustering ──────────────────────────────────────────────────────

def apply_kmeans(features_scaled: np.ndarray, n_clusters: int = 30):
    """
    Apply K-Means clustering to student feature vectors.

    The number of clusters equals the number of available exam rooms so
    that each cluster can be directly mapped to one room.

    Args:
        features_scaled: Scaled feature matrix (n_students × n_features).
        n_clusters:       Number of clusters (default = 30 rooms).

    Returns:
        tuple: (cluster_labels array, fitted KMeans model)
    """
    kmeans = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        max_iter=300,
        random_state=42,
    )
    labels = kmeans.fit_predict(features_scaled)
    return labels, kmeans


def find_optimal_clusters(features_scaled: np.ndarray,
                           k_range=range(10, 35)) -> list:
    """
    Compute inertia for a range of k values (elbow method).

    Args:
        features_scaled: Scaled features.
        k_range:          Range of k values to test.

    Returns:
        list of float: Inertia values corresponding to each k.
    """
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, init="k-means++", n_init=5,
                    random_state=42)
        km.fit(features_scaled)
        inertias.append(km.inertia_)
    return inertias


# ─── Seating Plan Generation ─────────────────────────────────────────────────

def generate_seating_plan(student_df: pd.DataFrame,
                           cluster_labels: np.ndarray) -> pd.DataFrame:
    """
    Assign students to rooms based on their cluster label.

    Each cluster is mapped to one room; if a cluster exceeds room
    capacity the overflow students are moved to the next available
    room slot.

    Args:
        student_df:     Student records (index aligned).
        cluster_labels: Cluster label for each student.

    Returns:
        pd.DataFrame: student_df augmented with [cluster, room, seat_no].
    """
    df = student_df.copy()
    df["cluster"] = cluster_labels

    # Build room-capacity map
    room_cap = {ROOM_NAMES[i]: ROOM_CAPACITIES[i] for i in range(30)}
    room_fill = {r: 0 for r in ROOM_NAMES}      # seats already filled
    room_idx  = 0                                # pointer to current room

    # Map cluster → primary room (cluster i → Room-i)
    cluster_to_room = {}
    for c in range(30):
        cluster_to_room[c] = ROOM_NAMES[c % 30]

    assigned_rooms = []
    assigned_seats = []

    for _, row in df.iterrows():
        target_room = cluster_to_room[row["cluster"]]

        # If primary room is full, find next room with space
        if room_fill[target_room] >= room_cap[target_room]:
            for room in ROOM_NAMES:
                if room_fill[room] < room_cap[room]:
                    target_room = room
                    break

        room_fill[target_room] += 1
        assigned_rooms.append(target_room)
        assigned_seats.append(room_fill[target_room])

    df["room"]    = assigned_rooms
    df["seat_no"] = assigned_seats
    return df


# ─── Faculty Allocation ───────────────────────────────────────────────────────

def allocate_faculty(seating_df: pd.DataFrame,
                     faculty_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign faculty members to each room based on the dominant domain
    present in that room.

    Each room receives two faculty members:
      - Primary: from the dominant domain.
      - Secondary: from another domain for cross-supervision.

    Args:
        seating_df: Seating plan with room assignments.
        faculty_df: Faculty records.

    Returns:
        pd.DataFrame: One row per room with faculty assignments.
    """
    # Determine dominant domain per room
    room_domain = (
        seating_df.groupby("room")["domain"]
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={"domain": "dominant_domain"})
    )

    # Keep a cyclic iterator per domain for round-robin assignment
    faculty_iter = {
        d: iter(faculty_df[faculty_df["domain"] == d]["name"].tolist() * 10)
        for d in DOMAINS
    }

    allocations = []
    for _, row in room_domain.iterrows():
        primary_domain = row["dominant_domain"]
        # Secondary domain: pick a different domain
        secondary_domain = random.choice(
            [d for d in DOMAINS if d != primary_domain]
        )
        allocations.append({
            "room":             row["room"],
            "dominant_domain":  primary_domain,
            "primary_faculty":  next(faculty_iter[primary_domain]),
            "secondary_faculty":next(faculty_iter[secondary_domain]),
        })

    return pd.DataFrame(allocations)


# ─── Reporting ────────────────────────────────────────────────────────────────

def generate_report(seating_df: pd.DataFrame,
                    faculty_alloc: pd.DataFrame) -> str:
    """
    Build a formatted text report summarising the seating and faculty plan.

    Args:
        seating_df:   Complete seating plan.
        faculty_alloc: Faculty allocation per room.

    Returns:
        str: Multi-line report string.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("   EXAM MANAGEMENT SYSTEM — SEATING & FACULTY REPORT")
    lines.append("=" * 70)

    total_students = len(seating_df)
    lines.append(f"\n  Total Students  : {total_students}")
    lines.append(f"  Total Rooms     : {len(ROOM_NAMES)}")
    lines.append(f"  Total Faculty   : {len(faculty_alloc) * 2} (2 per room)\n")

    lines.append("-" * 70)
    lines.append(f"{'Room':<12} {'Capacity':<10} {'Assigned':<10} "
                 f"{'Dom. Domain':<26} {'Primary Faculty':<20} {'Secondary Faculty'}")
    lines.append("-" * 70)

    room_counts = seating_df.groupby("room").size().reset_index(name="count")
    merged = faculty_alloc.merge(room_counts, on="room", how="left")

    room_cap_map = {ROOM_NAMES[i]: ROOM_CAPACITIES[i] for i in range(30)}

    for _, r in merged.iterrows():
        cap = room_cap_map.get(r["room"], "?")
        lines.append(
            f"{r['room']:<12} {cap:<10} {r['count']:<10} "
            f"{r['dominant_domain']:<26} {r['primary_faculty']:<20} "
            f"{r['secondary_faculty']}"
        )

    lines.append("\n" + "=" * 70)
    lines.append("  DOMAIN DISTRIBUTION ACROSS BATCHES")
    lines.append("=" * 70)

    pivot = (
        seating_df.groupby(["domain", "batch"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    lines.append(pivot.to_string(index=False))

    lines.append("\n" + "=" * 70)
    lines.append("  CLUSTER SUMMARY (students per cluster)")
    lines.append("=" * 70)
    cluster_summary = (
        seating_df.groupby("cluster")
        .agg(count=("student_id", "size"),
             domains=("domain",  lambda x: ", ".join(x.unique()[:2])))
        .reset_index()
    )
    lines.append(cluster_summary.to_string(index=False))
    lines.append("=" * 70)

    return "\n".join(lines)


# ─── Visualisation Helpers ───────────────────────────────────────────────────

def plot_elbow(k_range, inertias, ax):
    """Plot the elbow curve for optimal k selection."""
    ax.clear()
    ax.plot(list(k_range), inertias, "o-", color="#1f77b4", linewidth=2)
    ax.set_title("Elbow Method — Optimal k", fontsize=12, fontweight="bold")
    ax.set_xlabel("Number of Clusters (k)")
    ax.set_ylabel("Inertia")
    ax.grid(True, linestyle="--", alpha=0.5)


def plot_clusters_pca(features_scaled, labels, ax):
    """Project features to 2D via PCA and colour-code by cluster."""
    pca  = PCA(n_components=2, random_state=42)
    pts  = pca.fit_transform(features_scaled)
    scatter = ax.scatter(
        pts[:, 0], pts[:, 1],
        c=labels, cmap="tab20", alpha=0.6, s=8
    )
    ax.set_title("K-Means Clusters (PCA projection)", fontsize=12,
                 fontweight="bold")
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")


def plot_domain_distribution(seating_df, ax):
    """Stacked bar — students per domain × batch."""
    pivot = (
        seating_df.groupby(["domain", "batch"])
        .size()
        .unstack(fill_value=0)
    )
    pivot.plot(kind="bar", ax=ax, colormap="Set2", width=0.8)
    ax.set_title("Students per Domain × Batch", fontsize=12,
                 fontweight="bold")
    ax.set_xlabel("Domain")
    ax.set_ylabel("Number of Students")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(title="Batch", fontsize=8)


def plot_room_utilisation(seating_df, ax):
    """Horizontal bar — room fill vs capacity."""
    room_counts = seating_df.groupby("room").size()
    caps = pd.Series(
        {ROOM_NAMES[i]: ROOM_CAPACITIES[i] for i in range(30)}
    )
    ax.barh(room_counts.index, caps[room_counts.index],
            color="#d9d9d9", label="Capacity")
    ax.barh(room_counts.index, room_counts.values,
            color="#2196F3", alpha=0.85, label="Assigned")
    ax.set_title("Room Utilisation", fontsize=12, fontweight="bold")
    ax.set_xlabel("Students")
    ax.legend(fontsize=8)
    ax.tick_params(axis="y", labelsize=7)


# ─── GUI Application ─────────────────────────────────────────────────────────

class ExamManagementApp(tk.Tk):
    """
    Main Tkinter application window for the Exam Management System.

    Provides controls to:
      - Generate / reload data
      - Run K-Means clustering with a selectable k
      - View seating plan and faculty allocations
      - Display four analytical charts
      - Export the full report to a text file
    """

    def __init__(self):
        super().__init__()
        self.title("Automated Exam Management System — K-Means Clustering")
        self.geometry("1280x820")
        self.configure(bg="#1a1a2e")
        self.resizable(True, True)

        # Data holders
        self.student_df    : pd.DataFrame | None = None
        self.faculty_df    : pd.DataFrame | None = None
        self.seating_df    : pd.DataFrame | None = None
        self.faculty_alloc : pd.DataFrame | None = None
        self.features_scaled = None
        self.labels          = None

        self._build_ui()

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self):
        """Construct all widgets."""
        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(self, bg="#16213e", pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text="🏫  Automated Exam Management System",
            font=("Consolas", 18, "bold"),
            fg="#e94560", bg="#16213e",
        ).pack()
        tk.Label(
            header,
            text="K-Means Clustering Module",
            font=("Consolas", 10),
            fg="#a8b2d8", bg="#16213e",
        ).pack()

        # ── Main layout ───────────────────────────────────────────────────
        main = tk.Frame(self, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # Left panel: controls + tables
        left = tk.Frame(main, bg="#16213e", width=400)
        left.pack(side="left", fill="both", padx=(0, 5))
        left.pack_propagate(False)

        # Right panel: charts
        right = tk.Frame(main, bg="#1a1a2e")
        right.pack(side="left", fill="both", expand=True)

        self._build_controls(left)
        self._build_tables(left)
        self._build_charts(right)

    def _build_controls(self, parent):
        """Control buttons and k-slider."""
        ctrl = tk.LabelFrame(
            parent, text=" Controls ", bg="#16213e",
            fg="#e94560", font=("Consolas", 10, "bold"),
            labelanchor="nw", bd=1, relief="groove",
        )
        ctrl.pack(fill="x", padx=8, pady=8)

        # k slider
        k_frame = tk.Frame(ctrl, bg="#16213e")
        k_frame.pack(fill="x", padx=6, pady=4)
        tk.Label(k_frame, text="Number of Clusters (k):",
                 fg="#a8b2d8", bg="#16213e",
                 font=("Consolas", 9)).pack(side="left")
        self.k_var = tk.IntVar(value=30)
        self.k_label = tk.Label(k_frame, text="30", fg="#e94560",
                                bg="#16213e", font=("Consolas", 9, "bold"),
                                width=3)
        self.k_label.pack(side="right")
        k_slider = tk.Scale(
            ctrl, from_=10, to=30, orient="horizontal",
            variable=self.k_var, bg="#16213e", fg="#a8b2d8",
            troughcolor="#0f3460", highlightthickness=0,
            command=lambda v: self.k_label.config(text=v),
        )
        k_slider.pack(fill="x", padx=6)

        btn_cfg = dict(
            bg="#e94560", fg="white",
            font=("Consolas", 9, "bold"),
            relief="flat", cursor="hand2", pady=4,
        )

        tk.Button(ctrl, text="▶  Generate Data & Run Clustering",
                  command=self._run_pipeline, **btn_cfg).pack(
            fill="x", padx=6, pady=3)

        tk.Button(ctrl, text="📋  View Seating Plan",
                  command=self._show_seating, **btn_cfg).pack(
            fill="x", padx=6, pady=3)

        tk.Button(ctrl, text="👨‍🏫  View Faculty Allocation",
                  command=self._show_faculty, **btn_cfg).pack(
            fill="x", padx=6, pady=3)

        tk.Button(ctrl, text="📄  Export Full Report",
                  command=self._export_report, **btn_cfg).pack(
            fill="x", padx=6, pady=3)

        # Status bar
        self.status_var = tk.StringVar(value="Ready — click 'Generate Data & Run Clustering'")
        tk.Label(ctrl, textvariable=self.status_var,
                 fg="#64ffda", bg="#16213e",
                 font=("Consolas", 8), wraplength=360,
                 justify="left").pack(padx=6, pady=(2, 6))

    def _build_tables(self, parent):
        """Summary statistics table."""
        tbl_frame = tk.LabelFrame(
            parent, text=" Summary Statistics ", bg="#16213e",
            fg="#e94560", font=("Consolas", 10, "bold"),
            labelanchor="nw", bd=1, relief="groove",
        )
        tbl_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cols = ("Metric", "Value")
        self.summary_tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings", height=14
        )
        for c in cols:
            self.summary_tree.heading(c, text=c)
            self.summary_tree.column(c, width=160, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#0f3460", foreground="#a8b2d8",
            fieldbackground="#0f3460", rowheight=22,
            font=("Consolas", 9),
        )
        style.configure("Treeview.Heading",
                        background="#16213e", foreground="#e94560",
                        font=("Consolas", 9, "bold"))

        sb = ttk.Scrollbar(tbl_frame, orient="vertical",
                           command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=sb.set)
        self.summary_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _build_charts(self, parent):
        """Four matplotlib charts embedded in Tkinter."""
        self.fig, self.axes = plt.subplots(2, 2, figsize=(9, 6))
        self.fig.patch.set_facecolor("#1a1a2e")
        for ax in self.axes.flat:
            ax.set_facecolor("#0f3460")
            ax.tick_params(colors="#a8b2d8")
            for spine in ax.spines.values():
                spine.set_edgecolor("#16213e")

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.fig.tight_layout(pad=2)

    # ── Pipeline ──────────────────────────────────────────────────────────

    def _run_pipeline(self):
        """Execute the full data → cluster → seat → allocate pipeline."""
        self.status_var.set("⏳ Generating student and faculty data…")
        self.update()

        # 1. Data generation
        self.student_df = generate_student_data()
        self.faculty_df = generate_faculty_data()

        # 2. Preprocessing
        self.features_scaled, _, _, _ = preprocess_data(self.student_df)

        # 3. Clustering
        k = self.k_var.get()
        self.status_var.set(f"⏳ Running K-Means with k={k}…")
        self.update()
        self.labels, self.kmeans_model = apply_kmeans(
            self.features_scaled, n_clusters=k
        )

        # 4. Seating plan
        self.status_var.set("⏳ Generating seating plan…")
        self.update()
        self.seating_df = generate_seating_plan(self.student_df, self.labels)

        # 5. Faculty allocation
        self.status_var.set("⏳ Allocating faculty…")
        self.update()
        self.faculty_alloc = allocate_faculty(self.seating_df, self.faculty_df)

        # 6. Update summary table
        self._update_summary_table()

        # 7. Refresh charts
        self._refresh_charts()

        self.status_var.set(
            f"✅ Done! {len(self.student_df):,} students clustered into "
            f"{k} groups across {len(ROOM_NAMES)} rooms."
        )

    def _update_summary_table(self):
        """Populate the summary statistics treeview."""
        for row in self.summary_tree.get_children():
            self.summary_tree.delete(row)

        rows = [
            ("Total Students",    f"{len(self.student_df):,}"),
            ("Total Domains",     str(len(DOMAINS))),
            ("Total Batches",     str(len(BATCHES))),
            ("Num Clusters (k)",  str(self.k_var.get())),
            ("Total Rooms",       str(len(ROOM_NAMES))),
            ("Total Faculty",     str(len(self.faculty_df))),
            ("Avg Room Fill",
             f"{self.seating_df.groupby('room').size().mean():.1f}"),
            ("Max Room Fill",
             str(self.seating_df.groupby("room").size().max())),
            ("Min Room Fill",
             str(self.seating_df.groupby("room").size().min())),
        ]
        for domain in DOMAINS:
            cnt = (self.student_df["domain"] == domain).sum()
            rows.append((f"  {domain[:20]}", f"{cnt:,}"))

        for m, v in rows:
            self.summary_tree.insert("", "end", values=(m, v))

    def _refresh_charts(self):
        """Redraw all four charts with current data."""
        ax = self.axes

        # Chart 1: Elbow curve
        k_range = range(10, 31)
        inertias = find_optimal_clusters(self.features_scaled, k_range)
        plot_elbow(k_range, inertias, ax[0][0])
        ax[0][0].set_facecolor("#0f3460")
        ax[0][0].tick_params(colors="#a8b2d8")
        ax[0][0].title.set_color("#e94560")

        # Chart 2: PCA cluster scatter
        plot_clusters_pca(self.features_scaled, self.labels, ax[0][1])
        ax[0][1].set_facecolor("#0f3460")
        ax[0][1].tick_params(colors="#a8b2d8")
        ax[0][1].title.set_color("#e94560")

        # Chart 3: Domain × Batch distribution
        plot_domain_distribution(self.seating_df, ax[1][0])
        ax[1][0].set_facecolor("#0f3460")
        ax[1][0].tick_params(colors="#a8b2d8")
        ax[1][0].title.set_color("#e94560")

        # Chart 4: Room utilisation
        plot_room_utilisation(self.seating_df, ax[1][1])
        ax[1][1].set_facecolor("#0f3460")
        ax[1][1].tick_params(colors="#a8b2d8")
        ax[1][1].title.set_color("#e94560")

        self.fig.tight_layout(pad=2)
        self.canvas.draw()

    # ── Pop-up Windows ────────────────────────────────────────────────────

    def _show_seating(self):
        """Open a window showing the full seating plan table."""
        if self.seating_df is None:
            messagebox.showwarning("No Data", "Run the pipeline first.")
            return

        win = tk.Toplevel(self)
        win.title("Seating Plan")
        win.geometry("900x500")
        win.configure(bg="#1a1a2e")

        cols = ["roll_no", "name", "batch", "domain", "cluster",
                "room", "seat_no"]
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=120, anchor="center")

        for _, row in self.seating_df.iterrows():
            tree.insert("", "end",
                        values=[row[c] for c in cols])

        vsb = ttk.Scrollbar(win, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(win, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

    def _show_faculty(self):
        """Open a window showing faculty allocations per room."""
        if self.faculty_alloc is None:
            messagebox.showwarning("No Data", "Run the pipeline first.")
            return

        win = tk.Toplevel(self)
        win.title("Faculty Allocation")
        win.geometry("750x450")
        win.configure(bg="#1a1a2e")

        cols = list(self.faculty_alloc.columns)
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=160, anchor="center")

        for _, row in self.faculty_alloc.iterrows():
            tree.insert("", "end", values=list(row))

        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    def _export_report(self):
        """Generate and save the full text report to disk."""
        if self.seating_df is None or self.faculty_alloc is None:
            messagebox.showwarning("No Data", "Run the pipeline first.")
            return

        report_text = generate_report(self.seating_df, self.faculty_alloc)

        filepath = "exam_management_report.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)

        # Also show in a pop-up
        win = tk.Toplevel(self)
        win.title("Full Report")
        win.geometry("860x600")
        win.configure(bg="#1a1a2e")

        st = scrolledtext.ScrolledText(
            win, bg="#0f3460", fg="#a8b2d8",
            font=("Consolas", 9), wrap="none",
        )
        st.insert("1.0", report_text)
        st.configure(state="disabled")
        st.pack(fill="both", expand=True, padx=6, pady=6)

        messagebox.showinfo(
            "Exported",
            f"Report saved to:\n{filepath}"
        )


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ExamManagementApp()
    app.mainloop()