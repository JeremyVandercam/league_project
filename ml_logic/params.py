import os
import numpy as np

####################  VARIABLES  ##################
GCP_PROJECT = os.environ["GCP_PROJECT"]
BQ_DATASET = os.environ["BQ_DATASET"]


##################  CONSTANTS  #####################
LOCAL_DATA_PATH = os.path.join(
    os.path.expanduser("~"), "code", "JeremyVandercam", "league_project"
)
DOCKER_IMAGE = "league_project"

LOCAL_REGISTRY_PATH = os.path.join(
    os.path.expanduser("~"), "code", "JeremyVandercam", "league_project"
)
