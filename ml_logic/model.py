import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pandas as pd
import numpy as np



def train_model(X:pd.DataFrame, y:pd.DataFrame) ->np.array|float:

   # Split data into train, test and validation sets
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size = 0.3, random_state = 42)  # TEST = 30%

    # Use the same function above for the validation set
    X_test, X_val, y_test, y_val = train_test_split(
    X_test, y_test, test_size = 0.3, random_state = 42)  # TEST = 15%

    xgb_cl = XGBClassifier(max_depth=10, n_estimators=100, learning_rate=0.1,eval_metric="auc")

    xgb_cl.fit(X_train, y_train,
    # evaluate loss at each iteration
    eval_set=[(X_train, y_train), (X_val, y_val)],
    # stop iterating when eval loss increases 5 times in a row
    early_stopping_rounds=5)

    y_pred = xgb_cl.predict(X_test)

    score = roc_auc_score(y_test,y_pred)

    return y_pred, score
