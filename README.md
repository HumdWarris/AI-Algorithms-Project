# AI-Algorithms-Project
A 4-module AI lab project covering search algorithms (BFS/DFS/UCS/A*) for robot navigation, CSP-based Sudoku solving (AC-3 &amp; Backtracking), K-Means clustering for exam management, and Perceptron vs Delta Rule comparison. Built in Python with Tkinter GUIs.

🤖 Artificial Intelligence – Semester Project
Module-1:
<img width="975" height="797" alt="image" src="https://github.com/user-attachments/assets/c7ac0d6d-dfde-4ad0-a95f-478f8f166fd2" />

Module-2:
<img width="975" height="1085" alt="image" src="https://github.com/user-attachments/assets/a6f1b255-5c5a-46bf-98fa-a6699df9daed" />

Module-3:
<img width="975" height="648" alt="image" src="https://github.com/user-attachments/assets/21f88626-6472-423a-95cf-d8e5be7eee1f" />

Module-4:
<img width="975" height="915" alt="image" src="https://github.com/user-attachments/assets/7c879c61-2f3f-43b9-af4d-292b5c6c89f6" />



A 4-module AI lab project covering search algorithms, constraint satisfaction, unsupervised learning, and neural learning rules — each with a working Python implementation and GUI.

Authors: Muhammad Humd (24F-0542) & Muhammad Hammad Abid (24F-0612)

Course: Artificial Intelligence Lab — University of Management and Technology (UMT)


📦 Modules Overview

ModuleTopicAlgorithm(s)GUI1Intelligent Urban Delivery RobotBFS, DFS, UCS, Greedy, A*✅ Tkinter2Sudoku Puzzle SolverAC-3, Backtracking (CSP)✅ Tkinter3Automated Exam Management SystemK-Means Clustering✅ Tkinter4Perceptron vs Delta RulePerceptron, Delta Rule❌ Console


🗂️ Repository Structure

AI-Semester-Project/
├── README.md
├── module1/
│   ├── module1_delivery_robot.py
│   └── Module1_Report.docx
├── module2/
│   ├── module2_sudoku_solver.py
│   └── Module2_Report.docx
├── module3/
│   ├── AI-MOD-3.py
│   └── Module3_Report.docx
└── module4/
    ├── module4_perceptron_delta.py
    └── Module4_Report.docx


🚚 Module 1 — Intelligent Urban Delivery Robot

A robot navigates a 15×15 grid from a base station to 5 delivery points, avoiding buildings and traffic zones. Five search algorithms are implemented and visually compared.

Algorithms: BFS · DFS · UCS · Greedy Best-First · A*

Grid Elements:


🟦 Base Station — robot's starting point
🟩 Delivery Points — 5 targets to reach
⬛ Buildings — impassable obstacles (~20% of grid)
🟨 Traffic Zones — high-cost traversal cells


Features:


Live path animation showing explored nodes and final route
Algorithm selector — switch between all 5 with one click
Cost and time comparison across algorithms
Reproducible layout using fixed random seed


How to run:

bashpip install tkinter
python module1/module1_delivery_robot.py


🧩 Module 2 — Sudoku Puzzle Solver (CSP)

Solves Sudoku puzzles using two Constraint Satisfaction Problem (CSP) algorithms. A GUI lets the user pick difficulty, puzzle, and solver.

Algorithms:


AC-3 (Arc Consistency Algorithm 3) — reduces domains before solving
Backtracking Search — recursive constraint-based solving


Features:


12 built-in puzzles — 4 per difficulty (Easy / Medium / Hard)
Hint system — fills one correct cell on demand
Solve time displayed for both algorithms side-by-side


How to run:

bashpython module2/module2_sudoku_solver.py


🏫 Module 3 — Automated Exam Management System

Uses K-Means Clustering to group ~2,500 university students by domain and batch, then auto-generates a complete exam seating plan and faculty allocation across 30 rooms.

Dataset: Synthetic — 5 domains × 5 batches (~2,500 students total)

Domains: Computer Science · Artificial Intelligence · Business Analytics · Software Engineering · Electrical Engineering

Pipeline:


Generate synthetic student & faculty data
Encode and scale features (domain + batch)
Apply K-Means (k=10–30, selectable via slider)
Assign students to rooms respecting capacity limits
Allocate 2 faculty per room (primary + secondary domain)
Export full report to exam_management_report.txt


Charts (live in GUI):


Elbow curve for optimal k selection
PCA 2D cluster scatter plot
Students per domain × batch (stacked bar)
Room utilisation (assigned vs capacity)


How to run:

bashpip install numpy pandas scikit-learn matplotlib
python module3/AI-MOD-3.py


🧠 Module 4 — Perceptron vs Delta Rule

Implements both learning rules from scratch (no sklearn for training) and compares their accuracy on the Iris dataset across multiple activation functions.

Dataset: Iris (binary classification — classes 0 and 1)

Models implemented:


Perceptron — weight update based on classification error
DeltaRule — gradient descent with continuous error minimization


Activation functions tested:

ModelActivationsPerceptronStep, Sigmoid, TanhDelta RuleSigmoid, Tanh, Linear

Key findings printed to console:


Training and testing accuracy per activation function
Comparison of convergence behavior
Analysis of when Perceptron vs Delta Rule is better suited


How to run:

bashpip install numpy pandas scikit-learn
python module4/module4_perceptron_delta.py


🛠️ Requirements

python >= 3.10
numpy
pandas
scikit-learn
matplotlib
tkinter (built-in with Python)

Install all at once:

bashpip install numpy pandas scikit-learn matplotlib
