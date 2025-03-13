FROM python:3-slim

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY ml_logic ml_logic/
COPY setup.py setup.py
RUN pip install .

CMD
