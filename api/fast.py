

from ml_logic.registry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.state.model = load_model()

@app.get("/predict")



@app.get("/")
def root():
    # $CHA_BEGIN
    return dict(greeting="LOL")
    # $CHA_END
