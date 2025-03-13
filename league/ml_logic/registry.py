import glob
import os
import xgboost as xgb

from league.ml_logic.params import LOCAL_REGISTRY_PATH


def save_model(model: xgb.Booster) -> str:
    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb.model")

    print(model_path)
    model.save_model(model_path)

    return model_path


def load_model():
    local_model_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb.model")

    if not local_model_path:
        return None

    params = {
        "booster": "gbtree",
        "lambda": 0.052732495448724846,
        "alpha": 4.795726650341036e-08,
        "max_depth": 9,
        "min_child_weight": 1,
        "eta": 0.5888238671975178,
        "gamma": 2.001633795154716e-05,
        "subsample": 0.9437634512257028,
        "colsample_bytree": 0.48419223461881844,
    }

    latest_model = xgb.Booster(params)
    latest_model.load_model(local_model_path)

    return latest_model
