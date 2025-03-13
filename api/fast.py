import pandas as pd
import numpy as np
import xgboost as xgb

from ml_logic.registry import load_model

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.state.model = load_model()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/predict")
def predict_proba(
    side: float = 1.0, firstblood: float = 0.0, firstdragon: float = 0.0, firstherald: float = 1.0,
    firstbaron: float = 1.0, firsttower: float = 0.0, firstmidtower: float = 0.0, firsttothreetowers: float = 0.0,
    turretplates: float = 3.0, opp_turretplates: float = 2.0, goldat10: float = 15071.0, xpat10: float = 18472.0, csat10: float = 346.0,
    opp_goldat10: float = 14898.0, opp_xpat10: float = 19153.0, opp_csat10: float = 349.0, golddiffat10: float = 173.0,
    xpdiffat10: float = -681.0, csdiffat10: float = -3.0, killsat10: float = 0.0, assistsat10: float = 0.0, deathsat10: float = 0.0,
    opp_killsat10: float = 0.0, opp_assistsat10: float = 0.0, opp_deathsat10: float = 0.0, goldat15: float = 22726.0,
    xpat15: float = 28780.0, csat15: float = 540.0, opp_goldat15: float = 23480.0, opp_xpat15: float = 30504.0, opp_csat15: float = 545.0,
    golddiffat15: float = -754.0, xpdiffat15: float = -1724.0, csdiffat15: float = -5.0, killsat15: float = 0.0,
    assistsat15: float = 0.0, deathsat15: float = 2.0, opp_killsat15: float = 2.0, opp_assistsat15: float = 2.0,
    opp_deathsat15: float = 0.0, goldat20: float = 30923.0, xpat20: float = 38143.0, csat20: float = 669.0,
    opp_goldat20: float = 33135.0, opp_xpat20: float = 42547.0, opp_csat20: float = 696.0, golddiffat20: float = -2212.0,
    xpdiffat20: float = -4404.0, csdiffat20: float = -27.0, killsat20: float = 3.0, assistsat20: float = 9.0, deathsat20: float = 6.0,
    opp_killsat20: float = 6.0, opp_assistsat20: float = 13.0, opp_deathsat20: float = 3.0, goldat25: float = 37681.0,
    xpat25: float = 47022.0, csat25: float = 775.0, opp_goldat25: float = 46904.0, opp_xpat25: float = 59120.0, opp_csat25: float = 869.0,
    golddiffat25: float = -9223.0, xpdiffat25: float = -12098.0, csdiffat25: float = -94.0, killsat25: float = 5.0,
    assistsat25: float = 15.0, deathsat25: float = 17.0, opp_killsat25: float = 17.0, opp_assistsat25: float = 34.0,
    opp_deathsat25: float = 5.0):

    X_pred = pd.DataFrame(locals(), index=[0]).astype(float)

    model = load_model()
    assert model is not None

    d_test = xgb.DMatrix(X_pred, enable_categorical=True)
    predictions = model.predict(d_test)
    return {"pred": float(predictions[0])}


@app.get("/")
def root():
    return dict(greeting="LOL")
