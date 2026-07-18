"""
Progress Predictor

Loads the trained custom NumPy LSTM model and forecasts user weight progress
for the next 7 days using multi-step sequence predictions.
"""

from datetime import datetime, timedelta
from pathlib import Path
import joblib
import numpy as np


class ProgressPredictor:
    """
    Predicts weight trends using the trained Numpy LSTM cell.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_PATH = BASE_DIR / "trained_models" / "progress_lstm.pkl"

    def __init__(self):
        if self.MODEL_PATH.exists():
            self.params = joblib.load(self.MODEL_PATH)
        else:
            self.params = None

    def sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def forecast_weight(self, history_weights: list, dates: list, days_ahead=7) -> list:
        """
        Takes user's weight history and dates, and forecasts the next `days_ahead` days.
        Returns:
            list of dicts: [{'date': '19 Jul', 'weight': 78.5}, ...]
        """
        if self.params is None:
            return [{"date": "Error", "weight": "Model not trained"}]

        # We need at least 3 weight logs to make a projection, ideally 7.
        # If we have less than 7, we pad with the oldest weight to construct a 7-day input.
        if len(history_weights) < 3:
            return []

        weights_seq = list(history_weights)
        # Pad to length 7 if shorter
        while len(weights_seq) < 7:
            weights_seq.insert(0, weights_seq[0])
            
        # Only take the most recent 7 weights
        input_seq = np.array(weights_seq[-7:])

        # Extract LSTM parameters
        Wf, Wi, Wc, Wo, Wy = self.params["Wf"], self.params["Wi"], self.params["Wc"], self.params["Wo"], self.params["Wy"]
        bf, bi, bc, bo, by = self.params["bf"], self.params["bi"], self.params["bc"], self.params["bo"], self.params["by"]
        hidden_dim = self.params["hidden_dim"]

        forecasted_results = []
        last_date = datetime.strptime(dates[-1], "%d %b") if dates else datetime.now()

        # Multi-step forecasting loop
        # At each step, we normalize the input sequence, predict, denormalize, and append.
        for step in range(days_ahead):
            # Normalize sequence: subtract the first element of sequence (relative changes)
            base = input_seq[0]
            seq_norm = input_seq - base

            # Run LSTM forward pass
            h = np.zeros((hidden_dim, 1))
            c = np.zeros((hidden_dim, 1))

            for xt in seq_norm:
                xt_col = np.array([[xt]])
                concat = np.vstack((xt_col, h))

                f = self.sigmoid(np.dot(Wf, concat) + bf)
                i = self.sigmoid(np.dot(Wi, concat) + bi)
                c_bar = np.tanh(np.dot(Wc, concat) + bc)
                
                c = f * c + i * c_bar
                o = self.sigmoid(np.dot(Wo, concat) + bo)
                h = o * np.tanh(c)

            pred_norm = np.dot(Wy, h) + by
            pred_weight = round(float(pred_norm[0, 0] + base), 2)

            # Safeguard prediction values within physical bounds (e.g. 30kg to 250kg)
            pred_weight = max(30.0, min(250.0, pred_weight))

            # Compute next date
            next_date = last_date + timedelta(days=step + 1)
            forecasted_results.append({
                "date": next_date.strftime("%d %b"),
                "weight": pred_weight
            })

            # Slide window: slide out the oldest, append the predicted weight
            input_seq = np.append(input_seq[1:], pred_weight)

        return forecasted_results
