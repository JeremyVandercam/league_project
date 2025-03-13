import pandas as pd
import numpy as np
import xgboost as xgb
import optuna

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

from typing import Dict, Any

from league.ml_logic.registry import save_model


class XGBTrainer:
    def __init__(
        self, data: pd.DataFrame, target: pd.Series, test_size: float = 0.2, params={}
    ):
        self.data = data
        self.target = target
        self.test_size = test_size
        self.best_params: Dict[str, Any] = params
        self.model: xgb.Booster = None

    def _split_data(self):
        """Splits the dataset into training and validation sets."""
        return train_test_split(
            self.data, self.target, test_size=self.test_size, random_state=42
        )

    def _objective(self, trial: optuna.Trial) -> float:
        """Objective function for Optuna hyperparameter tuning."""
        X_train, X_val, y_train, y_val = self._split_data()
        d_train = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
        d_val = xgb.DMatrix(X_val, label=y_val, enable_categorical=True)

        params = {
            "objective": "binary:logistic",
            "booster": trial.suggest_categorical(
                "booster", ["gbtree", "gblinear", "dart"]
            ),
            "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
            "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
        }

        if params["booster"] in ["gbtree", "dart"]:
            params.update(
                {
                    "max_depth": trial.suggest_int("max_depth", 3, 9, step=2),
                    "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                    "eta": trial.suggest_float("eta", 1e-8, 1.0, log=True),
                    "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
                    "subsample": trial.suggest_float("subsample", 0.2, 1.0),
                    "colsample_bytree": trial.suggest_float(
                        "colsample_bytree", 0.2, 1.0
                    ),
                }
            )

        if params["booster"] == "dart":
            params.update(
                {
                    "rate_drop": trial.suggest_float("rate_drop", 1e-8, 1.0, log=True),
                    "one_drop": trial.suggest_categorical("one_drop", [0, 1]),
                    "skip_drop": trial.suggest_float("skip_drop", 1e-8, 1.0, log=True),
                }
            )

        bst = xgb.train(params, d_train)
        y_pred = bst.predict(d_val)
        return roc_auc_score(y_val, y_pred)

    def optimize_hyperparameters(
        self, n_trials: int = 100, timeout: int = 600
    ) -> Dict[str, Any]:
        """Runs Optuna hyperparameter tuning."""
        study = optuna.create_study(direction="maximize")
        study.optimize(self._objective, n_trials=n_trials, timeout=timeout)
        self.best_params = study.best_trial.params
        return self.best_params

    def train_model(self):
        """Trains the XGBoost model using the best parameters from optimization."""
        if not self.best_params:
            raise ValueError(
                "Hyperparameters have not been optimized. Run optimize_hyperparameters() first."
            )

        X_train, X_val, y_train, y_val = self._split_data()
        d_train = xgb.DMatrix(X_train, label=y_train)
        d_val = xgb.DMatrix(X_val, label=y_val)

        self.model = xgb.train(self.best_params, d_train)
        # saving the model
        save_model(self.model)

        return self.model

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts probabilities using the trained XGBoost model."""
        if not hasattr(self, "model"):
            raise ValueError("Model has not been trained. Run train_model() first.")

        d_test = xgb.DMatrix(X, enable_categorical=True)
        return self.model.predict(d_test)
