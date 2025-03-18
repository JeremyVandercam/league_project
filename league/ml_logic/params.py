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

##################  DATAFRAME  #####################
DTYPES_DICT = {
    "side": "int64",
    "result": "int64",
    "firstblood": "float64",
    "firstdragon": "float64",
    "firstbaron": "float64",
    "firsttower": "float64",
    "firsttothreetowers": "float64",
    "goldat10": "float64",
    "csat10": "float64",
    "opp_goldat10": "float64",
    "opp_csat10": "float64",
    "golddiffat10": "float64",
    "csdiffat10": "float64",
    "killsat10": "float64",
    "assistsat10": "float64",
    "deathsat10": "float64",
    "opp_killsat10": "float64",
    "opp_assistsat10": "float64",
    "opp_deathsat10": "float64",
    "goldat15": "float64",
    "csat15": "float64",
    "opp_goldat15": "float64",
    "opp_csat15": "float64",
    "golddiffat15": "float64",
    "csdiffat15": "float64",
    "killsat15": "float64",
    "assistsat15": "float64",
    "deathsat15": "float64",
    "opp_killsat15": "float64",
    "opp_assistsat15": "float64",
    "opp_deathsat15": "float64",
    "goldat20": "float64",
    "csat20": "float64",
    "opp_goldat20": "float64",
    "opp_csat20": "float64",
    "golddiffat20": "float64",
    "csdiffat20": "float64",
    "killsat20": "float64",
    "assistsat20": "float64",
    "deathsat20": "float64",
    "opp_killsat20": "float64",
    "opp_assistsat20": "float64",
    "opp_deathsat20": "float64",
    "goldat25": "float64",
    "csat25": "float64",
    "opp_goldat25": "float64",
    "opp_csat25": "float64",
    "golddiffat25": "float64",
    "csdiffat25": "float64",
    "killsat25": "float64",
    "assistsat25": "float64",
    "deathsat25": "float64",
    "opp_killsat25": "float64",
    "opp_assistsat25": "float64",
    "opp_deathsat25": "float64",
}
