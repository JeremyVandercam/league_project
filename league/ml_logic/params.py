import os

####################  VARIABLES  ##################
GCP_PROJECT = os.environ["GCP_PROJECT"]
BQ_DATASET = os.environ["BQ_DATASET"]
GCP_REGION = os.environ.get("GCP_REGION")
DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE")
DOCKER_MEMORY = os.environ.get("DOCKER_MEMORY")


##################  CONSTANTS  #####################
LOCAL_DATA_PATH = os.path.join(os.path.expanduser("~"), ".league_project", "data")
LOCAL_REGISTRY_PATH = os.path.join(os.path.expanduser("~"), ".league_project", "models")
os.makedirs(LOCAL_DATA_PATH, exist_ok=True)
os.makedirs(LOCAL_REGISTRY_PATH, exist_ok=True)
