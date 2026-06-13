import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


class Perceptron:
    def __init__(self, learning_rate=0.01, epochs=1000, activation='step'):
        self.lr = learning_rate
        self.epochs = epochs
        self.activation = activation

    def activate(self, x):
        if self.activation == 'step':
            return np.where(x >= 0, 1, 0)
        elif self.activation == 'sigmoid':
            return 1 / (1 + np.exp(-x))
        elif self.activation == 'tanh':
            return np.tanh(x)

    def fit(self, X, y):
        self.weights = np.zeros(X.shape[1])
        self.bias = 0

        for _ in range(self.epochs):
            for i in range(len(X)):
                linear_output = np.dot(X[i], self.weights) + self.bias
                y_pred = self.activate(linear_output)

                if self.activation != 'step':
                    y_pred = 1 if y_pred >= 0.5 else 0

                update = self.lr * (y[i] - y_pred)
                self.weights += update * X[i]
                self.bias += update

    def predict(self, X):
        linear_output = np.dot(X, self.weights) + self.bias
        y_pred = self.activate(linear_output)

        if self.activation == 'step':
            return y_pred
        return np.where(y_pred >= 0.5, 1, 0)


class DeltaRule:
    def __init__(self, learning_rate=0.01, epochs=1000, activation='sigmoid'):
        self.lr = learning_rate
        self.epochs = epochs
        self.activation = activation

    def activate(self, x):
        if self.activation == 'sigmoid':
            return 1 / (1 + np.exp(-x))
        elif self.activation == 'tanh':
            return np.tanh(x)
        elif self.activation == 'linear':
            return x

    def derivative(self, x):
        if self.activation == 'sigmoid':
            return x * (1 - x)
        elif self.activation == 'tanh':
            return 1 - x**2
        elif self.activation == 'linear':
            return 1

    def fit(self, X, y):
        self.weights = np.zeros(X.shape[1])
        self.bias = 0

        for _ in range(self.epochs):
            for i in range(len(X)):
                linear_output = np.dot(X[i], self.weights) + self.bias
                output = self.activate(linear_output)

                error = y[i] - output
                delta = error * self.derivative(output)

                self.weights += self.lr * delta * X[i]
                self.bias += self.lr * delta

    def predict(self, X):
        linear_output = np.dot(X, self.weights) + self.bias
        output = self.activate(linear_output)
        return np.where(output >= 0.5, 1, 0)


# ── Data Preparation ──────────────────────────────────────────────────────────
iris = load_iris()
X = iris.data
y = iris.target

binary_filter = y != 2
X = X[binary_filter]
y = y[binary_filter]

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Training & Collecting Results ─────────────────────────────────────────────
activation_functions = ['step', 'sigmoid', 'tanh']
delta_activations    = ['sigmoid', 'tanh', 'linear']

perc_train_accs, perc_test_accs = [], []
delta_train_accs, delta_test_accs = [], []

print("\nPERCEPTRON RESULTS")
print("-" * 50)

for act in activation_functions:
    perceptron = Perceptron(learning_rate=0.01, epochs=1000, activation=act)
    perceptron.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, perceptron.predict(X_train))
    test_acc  = accuracy_score(y_test,  perceptron.predict(X_test))

    perc_train_accs.append(train_acc)
    perc_test_accs.append(test_acc)

    print(f"Activation Function: {act}")
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy:  {test_acc:.4f}")
    print("-" * 50)

print("\nDELTA RULE RESULTS")
print("-" * 50)

for act in delta_activations:
    delta_model = DeltaRule(learning_rate=0.01, epochs=1000, activation=act)
    delta_model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, delta_model.predict(X_train))
    test_acc  = accuracy_score(y_test,  delta_model.predict(X_test))

    delta_train_accs.append(train_acc)
    delta_test_accs.append(test_acc)

    print(f"Activation Function: {act}")
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy:  {test_acc:.4f}")
    print("-" * 50)

# ── Graphs (separate window) ──────────────────────────────────────────────────
x1 = np.arange(len(activation_functions))   # positions for Perceptron bars
x2 = np.arange(len(delta_activations))      # positions for Delta Rule bars
bar_width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Model Accuracy Comparison", fontsize=14, fontweight='bold')

# --- Perceptron bar chart ---
ax1.bar(x1 - bar_width/2, perc_train_accs, bar_width, label='Train', color='steelblue')
ax1.bar(x1 + bar_width/2, perc_test_accs,  bar_width, label='Test',  color='coral')
ax1.set_title("Perceptron")
ax1.set_xlabel("Activation Function")
ax1.set_ylabel("Accuracy")
ax1.set_xticks(x1)
ax1.set_xticklabels(activation_functions)
ax1.set_ylim(0, 1.1)
ax1.legend()

# add value labels on bars
for i, (tr, te) in enumerate(zip(perc_train_accs, perc_test_accs)):
    ax1.text(i - bar_width/2, tr + 0.02, f"{tr:.2f}", ha='center', fontsize=8)
    ax1.text(i + bar_width/2, te + 0.02, f"{te:.2f}", ha='center', fontsize=8)

# --- Delta Rule bar chart ---
ax2.bar(x2 - bar_width/2, delta_train_accs, bar_width, label='Train', color='steelblue')
ax2.bar(x2 + bar_width/2, delta_test_accs,  bar_width, label='Test',  color='coral')
ax2.set_title("Delta Rule")
ax2.set_xlabel("Activation Function")
ax2.set_ylabel("Accuracy")
ax2.set_xticks(x2)
ax2.set_xticklabels(delta_activations)
ax2.set_ylim(0, 1.1)
ax2.legend()

for i, (tr, te) in enumerate(zip(delta_train_accs, delta_test_accs)):
    ax2.text(i - bar_width/2, tr + 0.02, f"{tr:.2f}", ha='center', fontsize=8)
    ax2.text(i + bar_width/2, te + 0.02, f"{te:.2f}", ha='center', fontsize=8)

plt.tight_layout()
plt.show()   # opens in a separate window

# ── Answers ───────────────────────────────────────────────────────────────────
print("\nANSWERS")
print("-" * 50)

print("1. Perceptron Learning Rule updates weights using classification errors and works for linearly separable data.")
print("   Delta Rule uses gradient descent to minimize loss and can handle continuous outputs.")

print("\n2. Activation functions affect learning behavior and accuracy.")
print("   Sigmoid provides smooth learning, tanh centers outputs around zero, and step works only for hard classification.")

print("\n3. Learning rate can be optimized using trial-and-error, decay methods, adaptive learning, or validation performance.")

print("\n4. Different train-test ratios affect model generalization.")
print("   Larger training data improves learning while larger testing data improves evaluation reliability.")

print("\n5. Challenges included implementing weight updates, handling activation functions, and stabilizing convergence.")
print("   These were solved through normalization and tuning epochs and learning rates.")

print("\n6. Perceptron is simple and fast but limited to linear problems.")
print("   Delta Rule is more flexible and stable but may require more computation.")