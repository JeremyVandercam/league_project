from sklearn.metrics import roc_auc_score
import xgboost as xgb

import optuna

from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


class XGBTrainer:
    def __init__(self, data, target):
        self.data = data
        self.target = target

    def train_model(self):
        def objective(trial):
            X_train, X_val, y_train, y_val = train_test_split(
                self.data, self.target, test_size=0.20
            )

            d_train = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
            d_val = xgb.DMatrix(X_val, label=y_val, enable_categorical=True)

            # Suggest values of the hyperparameters using a trial object.
            params = {
                "objective": "binary:logistic",
                "booster": trial.suggest_categorical(
                    "booster", ["gbtree", "gblinear", "dart"]
                ),
                "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
                "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
                # "subsample": trial.suggest_float("subsample", 0.2, 1.0),
                # "colsample_bytree": trial.suggest_float("colsample_bytree", 0.2, 1.0),
            }

            if params["booster"] in ["gbtree", "dart"]:
                # maximum depth of the tree, signifies complexity of the tree.
                params["max_depth"] = trial.suggest_int("max_depth", 3, 9, step=2)
                # minimum child weight, larger the term more conservative the tree.
                params["min_child_weight"] = trial.suggest_int(
                    "min_child_weight", 2, 10
                )
                params["eta"] = trial.suggest_float("eta", 1e-8, 1.0, log=True)
                # defines how selective algorithm is.
                params["gamma"] = trial.suggest_float("gamma", 1e-8, 1.0, log=True)
                params["grow_policy"] = trial.suggest_categorical(
                    "grow_policy", ["depthwise", "lossguide"]
                )

            if params["booster"] == "dart":
                params["sample_type"] = trial.suggest_categorical(
                    "sample_type", ["uniform", "weighted"]
                )
                params["normalize_type"] = trial.suggest_categorical(
                    "normalize_type", ["tree", "forest"]
                )
                params["rate_drop"] = trial.suggest_float(
                    "rate_drop", 1e-8, 1.0, log=True
                )
                params["skip_drop"] = trial.suggest_float(
                    "skip_drop", 1e-8, 1.0, log=True
                )

            bst = xgb.train(params, d_train)

            y_pred = bst.predict(d_val)
            auc = roc_auc_score(y_val, y_pred)
            return auc

        # Create a study object and optimize the objective function.
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=100, timeout=600)

        return study.best_trial
