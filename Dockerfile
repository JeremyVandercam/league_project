FROM python:3.10-buster

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY league league/
COPY setup.py setup.py
RUN pip install .

COPY models/xgb.model root/.league_project/models/xgb.model

CMD uvicorn league.api.fast:app --port=$PORT --host=0.0.0.0
