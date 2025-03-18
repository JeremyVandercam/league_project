import os

LOCAL_DATA_PATH = os.path.join(os.path.expanduser("~"), ".league_project", "data")
NUM_EPOCHS = int(os.environ["EPOCHS"])
COMET_API_KEY = os.environ["COMET_API_KEY"]
COMET_PROJECT_NAME = os.environ["COMET_PROJECT_NAME"]
COMET_MODEL_NAME = os.environ["COMET_MODEL_NAME"]
COMET_WORKSPACE_NAME = os.environ["COMET_WORKSPACE_NAME"]
ROBOFLOW_API_KEY = os.environ["ROBOFLOW_API_KEY"]
