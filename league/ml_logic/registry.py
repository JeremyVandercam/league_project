import json
import os
import xgboost as xgb

from league.ml_logic.params import LOCAL_REGISTRY_PATH


def save_model(model: xgb.Booster) -> str:
    """Save the model locally"""
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb.model")

    print(model_path)
    model.save_model(model_path)

    return model_path


def save_params(params: dict) -> str:
    """Save the model best parameters locally"""
    params_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb_params.json")

    with open(params_path, "w") as json_file:
        json.dump(params, json_file, indent=4)

    print(f"Best params saved as {params_path}")

    return params_path


def load_model() -> xgb.Booster:
    """Load model best and best parameters locally"""
    local_model_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb.model")
    local_params_path = os.path.join(LOCAL_REGISTRY_PATH, "xgb_params.json")

    if not local_model_path:
        return None
    if not local_params_path:
        return None

    # Read the JSON file and load it into a dictionary
    with open(local_params_path, "r") as json_file:
        params = json.load(json_file)

    if not params:
        return None

    latest_model = xgb.Booster(params)
    latest_model.load_model(local_model_path)

    return latest_model
