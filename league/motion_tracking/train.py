from ultralytics import YOLO

from league.motion_tracking.params import (
    LOCAL_DATA_PATH,
    COMET_WORKSPACE_NAME,
    COMET_MODEL_NAME,
    COMET_PROJECT_NAME,
    NUM_EPOCHS,
)
import os
import comet_ml
from comet_ml import API
from league.motion_tracking.data import load_data


# Function to train the model
def train_model(epochs: int = 10, img_size: int = 640):
    # Initialize Comet ML API connection
    api = API()
    comet_ml.init()

    # Try to use pretrained weights if available
    try:
        # Fetching the model from Comet ML
        models = api.get_model(
            workspace=COMET_WORKSPACE_NAME,
            model_name=COMET_MODEL_NAME,
        )

        # Get production model weights
        model_versions = models.find_versions(status="Production")
        latest_production_weights = model_versions[0]

        # Preparing local path for weights
        weights_path = os.path.join(LOCAL_DATA_PATH, "weights")
        os.makedirs(weights_path, exist_ok=True)

        # Downloading the weights
        models.download(
            version=latest_production_weights,
            output_folder=weights_path,
            expand=True,
        )

        # Load the model with the downloaded weights
        model = YOLO(os.path.join(weights_path, "best.pt"))
        model.train(resume=True)
        print("✅ Loaded weights from the comet ML")

    # If loading pretrained weights fails, initialize a new model
    except Exception as error:
        print(f"❌ Could not load weights: {error}")
        params = {
            "data": os.path.join(LOCAL_DATA_PATH, "data.yaml"),
            "epochs": epochs,
            "imgsz": img_size,
            "patience": 20,
        }
        device = os.environ.get("DEVICE", "CUDA")
        if device == "mps":
            params.update({"device": "mps"})

        # Initialize a new YOLO model with default weights
        model = YOLO("yolo11m.pt")
        model.train(**params)

    # Save the trained model weights to Comet ML
    experiments = api.get(
        workspace=COMET_WORKSPACE_NAME, project_name=COMET_PROJECT_NAME
    )

    # Registering the latest experiment and model
    current_experiment = experiments[-1]._name
    experiment = api.get(
        workspace=COMET_WORKSPACE_NAME,
        project_name=COMET_PROJECT_NAME,
        experiment=current_experiment,
    )

    # Sort list of experiments by one of the metrics to find best one
    experiments.sort(
        key=lambda each_experiment: (
            float(each_experiment.get_metrics_summary("metrics/mAP50(B)")["valueMax"])
            # If some experiment got stopped without any metric we want to skip it
            if isinstance(each_experiment.get_metrics_summary("metrics/mAP50(B)"), dict)
            else 0
        )
    )

    # get best experiment
    best_experiment_so_far = experiments[-1]._name

    # If current one is the best than move this model to production
    if current_experiment == best_experiment_so_far:
        experiment.register_model(COMET_MODEL_NAME, status="Production")
        print("✅ Registered current model as Production")
    else:
        experiment.register_model(COMET_MODEL_NAME)
        print("🖌️ Registered current model as history")


# Main execution
if __name__ == "__main__":
    load_data()
    train_model(epochs=NUM_EPOCHS)
