import xgboost as xgb

from league.ml_logic.preprocessor import expand_df, get_df_from_api_data
from league.ml_logic.registry import load_model

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

app = FastAPI()

app.state.model = load_model()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/predict")
def predict_proba(request: dict) -> dict:
    model = app.state.model
    assert model is not None

    predictions = {
        "game_ids": request["game_ids"],
        "start_time": request["startingTime"],
        "predictions": [],
    }

    for id in predictions["game_ids"]:
        data = get_df_from_api_data(id, request["startingTime"])

        data = expand_df(data)

        X = data.drop(columns=["minutes"])

        X_pred = xgb.DMatrix(X.fillna(0), enable_categorical=True)
        pred = model.predict(X_pred)

        predictions["predictions"].append(pred.tolist())

    return predictions


@app.get("/")
def root():
    return dict(greeting="LOL")
