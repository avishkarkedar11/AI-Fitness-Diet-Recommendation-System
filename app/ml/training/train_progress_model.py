"""
Train Progress Tracker (LSTM Time Series) Model

Generates synthetic weight history trajectories (weight loss, weight gain, and stability)
and trains a custom NumPy-based LSTM model using backpropagation through time (BPTT).
Saves the trained model parameters.
"""

from pathlib import Path
import joblib
import numpy as np


class LSTMCell:
    """
    A single-layer LSTM cell implemented in pure NumPy with backpropagation through time.
    """

    def __init__(self, input_dim=1, hidden_dim=4, output_dim=1):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Combine input_dim and hidden_dim for gate calculations
        concat_dim = input_dim + hidden_dim

        # Initialize weights with Xavier/Glorot initialization
        self.Wf = np.random.randn(hidden_dim, concat_dim) * np.sqrt(2.0 / concat_dim)
        self.Wi = np.random.randn(hidden_dim, concat_dim) * np.sqrt(2.0 / concat_dim)
        self.Wc = np.random.randn(hidden_dim, concat_dim) * np.sqrt(2.0 / concat_dim)
        self.Wo = np.random.randn(hidden_dim, concat_dim) * np.sqrt(2.0 / concat_dim)
        self.Wy = np.random.randn(output_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)

        self.bf = np.zeros((hidden_dim, 1))
        self.bi = np.zeros((hidden_dim, 1))
        self.bc = np.zeros((hidden_dim, 1))
        self.bo = np.zeros((hidden_dim, 1))
        self.by = np.zeros((output_dim, 1))

    def sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def sigmoid_derivative(self, val):
        # Expects val to be sigmoid output
        return val * (1.0 - val)

    def tanh_derivative(self, val):
        # Expects val to be tanh output
        return 1.0 - val ** 2

    def forward(self, X_seq):
        """
        Forward pass for a sequence of length T.
        X_seq shape: (seq_len, input_dim)
        Returns:
            y: predicted output (scalar/array)
            caches: dictionary containing states at each time step for backprop
        """
        seq_len = len(X_seq)
        
        # Caches to store states for backprop
        h_states = { -1: np.zeros((self.hidden_dim, 1)) }
        c_states = { -1: np.zeros((self.hidden_dim, 1)) }
        f_gates = {}
        i_gates = {}
        c_bar_gates = {}
        o_gates = {}
        concat_inputs = {}

        for t in range(seq_len):
            xt = X_seq[t].reshape(-1, 1)
            concat = np.vstack((xt, h_states[t-1]))
            concat_inputs[t] = concat

            f_gates[t] = self.sigmoid(np.dot(self.Wf, concat) + self.bf)
            i_gates[t] = self.sigmoid(np.dot(self.Wi, concat) + self.bi)
            c_bar_gates[t] = np.tanh(np.dot(self.Wc, concat) + self.bc)
            
            c_states[t] = f_gates[t] * c_states[t-1] + i_gates[t] * c_bar_gates[t]
            o_gates[t] = self.sigmoid(np.dot(self.Wo, concat) + self.bo)
            h_states[t] = o_gates[t] * np.tanh(c_states[t])

        y = np.dot(self.Wy, h_states[seq_len - 1]) + self.by

        caches = {
            "h": h_states,
            "c": c_states,
            "f": f_gates,
            "i": i_gates,
            "c_bar": c_bar_gates,
            "o": o_gates,
            "concat": concat_inputs,
            "seq_len": seq_len
        }

        return y[0, 0], caches

    def backward(self, caches, dy, lr=0.01):
        """
        Backpropagation through time (BPTT).
        dy: loss gradient with respect to prediction y
        """
        seq_len = caches["seq_len"]
        h_states = caches["h"]
        c_states = caches["c"]
        f_gates = caches["f"]
        i_gates = caches["i"]
        c_bar_gates = caches["c_bar"]
        o_gates = caches["o"]
        concat_inputs = caches["concat"]

        # Gradients
        dWy = np.dot(dy, h_states[seq_len - 1].T)
        dby = dy

        dWf, dWi, dWc, dWo = [np.zeros_like(W) for W in [self.Wf, self.Wi, self.Wc, self.Wo]]
        dbf, dbi, dbc, dbo = [np.zeros_like(b) for b in [self.bf, self.bi, self.bc, self.bo]]

        dh_next = np.zeros((self.hidden_dim, 1))
        dc_next = np.zeros((self.hidden_dim, 1))

        # Output gate gradient at step T
        dh_last = np.dot(self.Wy.T, dy)

        for t in reversed(range(seq_len)):
            dh = dh_last + dh_next if t == seq_len - 1 else dh_next
            
            # Gradient of hidden state through tanh of cell state
            tanh_c = np.tanh(c_states[t])
            do = dh * tanh_c
            do_input = self.sigmoid_derivative(o_gates[t]) * do

            # Cell state gradient
            dc = dh * o_gates[t] * self.tanh_derivative(tanh_c) + dc_next
            
            # Forget, input, candidate gate gradients
            df = dc * c_states[t-1]
            df_input = self.sigmoid_derivative(f_gates[t]) * df

            di = dc * c_bar_gates[t]
            di_input = self.sigmoid_derivative(i_gates[t]) * di

            dc_bar = dc * i_gates[t]
            dc_bar_input = self.tanh_derivative(c_bar_gates[t]) * dc_bar

            # Accumulate weight gradients
            concat = concat_inputs[t]
            dWf += np.dot(df_input, concat.T)
            dWi += np.dot(di_input, concat.T)
            dWc += np.dot(dc_bar_input, concat.T)
            dWo += np.dot(do_input, concat.T)

            # Accumulate bias gradients
            dbf += df_input
            dbi += di_input
            dbc += dc_bar_input
            dbo += do_input

            # Compute next state gradients (past in time)
            dconcat = (
                np.dot(self.Wf.T, df_input) +
                np.dot(self.Wi.T, di_input) +
                np.dot(self.Wc.T, dc_bar_input) +
                np.dot(self.Wo.T, do_input)
            )

            # Split concat back into dx_t and dh_{t-1}
            dh_next = dconcat[self.input_dim:]
            dc_next = f_gates[t] * dc

        # Clip gradients to prevent exploding gradients
        for g in [dWf, dWi, dWc, dWo, dWy, dbf, dbi, dbc, dbo, dby]:
            np.clip(g, -1.0, 1.0, out=g)

        # SGD Update
        self.Wf -= lr * dWf
        self.Wi -= lr * dWi
        self.Wc -= lr * dWc
        self.Wo -= lr * dWo
        self.Wy -= lr * dWy
        self.bf -= lr * dbf
        self.bi -= lr * dbi
        self.bc -= lr * dbc
        self.bo -= lr * dbo
        self.by -= lr * dby


class ProgressModelTrainer:
    """
    Simulates training data and trains the custom LSTM model.
    """

    MODEL_NAME = "progress_lstm.pkl"

    @classmethod
    def generate_synthetic_data(cls):
        """
        Generate synthetic daily weight logs for 100 users over 30 days.
        """
        np.random.seed(42)
        X_data = []
        y_data = []

        # Generate loss, gain, and maintenance trajectories
        for _ in range(120):
            # Start weight
            w = np.random.uniform(60, 100)
            goal = np.random.choice(["lose", "gain", "maintain"], p=[0.6, 0.2, 0.2])
            
            trajectory = []
            for _ in range(30):
                # Daily weight fluctuation
                noise = np.random.normal(0, 0.1)
                if goal == "lose":
                    w += -0.15 + noise
                elif goal == "gain":
                    w += 0.12 + noise
                else:
                    w += noise
                trajectory.append(w)
            
            # Create sequences of length 7 to predict the 8th day
            for i in range(len(trajectory) - 7):
                seq = np.array(trajectory[i:i+7])
                # Normalize seq by subtracting the first element to capture relative change
                base = seq[0]
                seq_norm = seq - base
                target_norm = trajectory[i+7] - base
                
                X_data.append(seq_norm)
                y_data.append(target_norm)

        return np.array(X_data), np.array(y_data)

    @classmethod
    def train(cls):
        print("=" * 60)
        print("Generating synthetic time-series weight logs...")
        print("=" * 60)
        
        X, y = cls.generate_synthetic_data()
        
        # Shuffle
        idx = np.arange(len(X))
        np.random.shuffle(idx)
        X, y = X[idx], y[idx]

        # Train/Test Split (80/20)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Create LSTM Cell
        lstm = LSTMCell(input_dim=1, hidden_dim=8, output_dim=1)

        print(f"Training Custom LSTM on {len(X_train)} sequences...")
        epochs = 15
        lr = 0.01

        for epoch in range(epochs):
            loss_sum = 0
            for i in range(len(X_train)):
                seq = X_train[i]  # shape (7,)
                target = y_train[i]

                # Forward
                pred, caches = lstm.forward(seq)
                
                # Compute loss (MSE)
                loss = 0.5 * (pred - target) ** 2
                loss_sum += loss

                # Backward
                dy = np.array([[pred - target]])
                lstm.backward(caches, dy, lr=lr)

            # Evaluate on Test Set
            test_loss_sum = 0
            for i in range(len(X_test)):
                pred, _ = lstm.forward(X_test[i])
                test_loss_sum += 0.5 * (pred - y_test[i]) ** 2

            train_rmse = np.sqrt((loss_sum * 2) / len(X_train))
            test_rmse = np.sqrt((test_loss_sum * 2) / len(X_test))

            print(f"Epoch {epoch+1:02d}/{epochs} | Train RMSE: {train_rmse:.4f} | Test RMSE: {test_rmse:.4f}")

        # Save model
        model_dir = Path(__file__).resolve().parent.parent / "trained_models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / cls.MODEL_NAME
        
        # We serialize the trained cell parameters
        model_params = {
            "Wf": lstm.Wf, "Wi": lstm.Wi, "Wc": lstm.Wc, "Wo": lstm.Wo, "Wy": lstm.Wy,
            "bf": lstm.bf, "bi": lstm.bi, "bc": lstm.bc, "bo": lstm.bo, "by": lstm.by,
            "hidden_dim": lstm.hidden_dim
        }
        joblib.dump(model_params, model_path)
        print(f"\nCustom LSTM trained parameters saved successfully at: {model_path}")
        print("=" * 60)


if __name__ == "__main__":
    ProgressModelTrainer.train()
