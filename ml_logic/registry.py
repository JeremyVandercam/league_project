import glob
import os
import xgboost as xgb


from ml_logic.params import *





def save_model(model: xgb.Booster) -> str:

    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models", "xgb.model")
    os.makedirs( os.path.join(LOCAL_REGISTRY_PATH, "models"), exist_ok=True)
    print(model_path)
    model.save_model(model_path)

    return model_path


def load_model():

    local_model_paths = os.path.join(LOCAL_REGISTRY_PATH, "models", "xgb.model")

    if not local_model_paths:
            return None

    bst = xgb.Booster()

    latest_model = bst.load_model(local_model_paths)

    return latest_model
