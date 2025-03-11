import xgboost as xgb
from sklearn.metrics import roc_auc_score


class XGBTrainer:
    def __init__(self, params):
        self.params = params

    def fit(self, dtrain, dval, y_val):
        print("Training XGB model")

        # Add evaluation metric and early stopping rounds to parameters
        early_stopping_rounds = 20
        evals = [(dtrain, "train"), (dval, "eval")]

        # Train the model with early stopping
        model = xgb.train(
            self.params,
            dtrain,
            num_boost_round=1590,
            evals=evals,
            early_stopping_rounds=early_stopping_rounds,
        )

        # Predict and calculate AUC
        y_pred = model.predict(dval, iteration_range=(0, model.best_iteration + 1))
        auc = roc_auc_score(y_val, y_pred)

        print(f"---AUC: {auc:.6f}")

        return auc
params = {
        "objective": "binary:logistic",
        "n_jobs": -1,
        "verbosity": 0
        "eval_metric": "auc",
        "random_state": SEED,
    }
auc = XGBTrainer(params).fit(dtrain, dval, y_val)
