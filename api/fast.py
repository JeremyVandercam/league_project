import pandas as pd
import numpy as np
import xgboost as xgb

from ml_logic.registry import load_model

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.state.model = load_model()

@app.get("/predict")

def predict_proba(
    side: str = "1.0", firstblood: str = "0.0", firstdragon: str = "0.0", firstherald: str = "1.0",
    firstbaron: str = "1.0", firsttower: str = "0.0", firstmidtower: str = "0.0", firsttothreetowers: str = "0.0",
    turretplates: str = "3.0", opp_turretplates: str = "2.0", goldat10: str = "15071.0", xpat10: str = "18472.0", csat10: str = "346.0",
    opp_goldat10: str = "14898.0", opp_xpat10: str = "19153.0", opp_csat10: str = "349.0", golddiffat10: str = "173.0",
    xpdiffat10: str = "-681.0", csdiffat10: str = "-3.0", killsat10: str = "0.0", assistsat10: str = "0.0", deathsat10: str = "0.0",
    opp_killsat10: str = "0.0", opp_assistsat10: str = "0.0", opp_deathsat10: str = "0.0", goldat15: str = "22726.0",
    xpat15: str = "28780.0", csat15: str = "540.0", opp_goldat15: str = "23480.0", opp_xpat15: str = "30504.0", opp_csat15: str = "545.0",
    golddiffat15: str = "-754.0", xpdiffat15: str = "-1724.0", csdiffat15: str = "-5.0", killsat15: str = "0.0",
    assistsat15: str = "0.0", deathsat15: str = "2.0", opp_killsat15: str = "2.0", opp_assistsat15: str = "2.0",
    opp_deathsat15: str = "0.0", goldat20: str = "30923.0", xpat20: str = "38143.0", csat20: str = "669.0",
    opp_goldat20: str = "33135.0", opp_xpat20: str = "42547.0", opp_csat20: str = "696.0", golddiffat20: str = "-2212.0",
    xpdiffat20: str = "-4404.0", csdiffat20: str = "-27.0", killsat20: str = "3.0", assistsat20: str = "9.0", deathsat20: str = "6.0",
    opp_killsat20: str = "6.0", opp_assistsat20: str = "13.0", opp_deathsat20: str = "3.0", goldat25: str = "37681.0",
    xpat25: str = "47022.0", csat25: str = "775.0", opp_goldat25: str = "46904.0", opp_xpat25: str = "59120.0", opp_csat25: str = "869.0",
    golddiffat25: str = "-9223.0", xpdiffat25: str = "-12098.0", csdiffat25: str = "-94.0", killsat25: str = "5.0",
    assistsat25: str = "15.0", deathsat25: str = "17.0", opp_killsat25: str = "17.0", opp_assistsat25: str = "34.0",
    opp_deathsat25: str = "5.0", row_type: str = "25"):


    X_pred = pd.DataFrame(locals(), index=[0])


    model = app.state.model
    assert model is not None


    d_test = xgb.DMatrix(X_pred, enable_categorical=True)

    prediction = model.predict(d_test)

    return {"pred": prediction}


@app.get("/")
def root():
    return dict(greeting="LOL")
