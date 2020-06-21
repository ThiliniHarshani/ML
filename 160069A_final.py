# -*- coding: utf-8 -*-
"""final

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15vwlzxnQaT7dRgMkcJaT67s3xbpqFJ5f
"""

# Code to read csv file into colaboratory:
!pip install -U -q PyDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline

import xgboost as xgb

from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import numpy as np
import pandas as pd
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
import matplotlib.pyplot as plt

# plt.style.use('classic')

dataset = drive.CreateFile({'id':'1zyy8RckILncBxCpADfGfMKc9Hc24U9Wt'}) # replace the id with id of file you want to access
dataset.GetContentFile('train.csv') 

testdata = drive.CreateFile({'id':'1UdFOWQVMUSlK9mW1DdMnZTmsUvW4gEIT'})
testdata.GetContentFile('test.csv') 

submission =drive.CreateFile({'id':'1PSxpyl3UdCf1AgirPla9KtTA5mC1BNyB'})
submission.GetContentFile('sample_submission.csv')

RANDOM_SEED = 40    # Set a random seed for reproducibility!

train_df = pd.read_csv("train.csv")
df = train_df.reindex(np.random.RandomState(seed=42).permutation(train_df.index))

def distance(lat1, lon1, lat2, lon2):
  
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    d = 6367 * c
    return d

df.dropna(thresh=5)

#adjusting columns

df['drop_time'] = pd.to_datetime(df.drop_time ,errors = "coerce")
df['pickup_time'] = pd.to_datetime(df.pickup_time ,errors = "coerce")

df['calcu_duration'] = (df.drop_time.dt.hour-df.pickup_time.dt.hour)*3600 + (df.drop_time.dt.minute-df.pickup_time.dt.minute)*60

df['pickup_time_hour'] = df.pickup_time.dt.hour

df['drop_time_hour'] =df.drop_time.dt.hour

df["distance"] =  distance(df["pick_lat"],df["pick_lon"],df["drop_lat"],df["drop_lon"])

df['pickup_time']=df['pickup_time'].astype(str)
df['drop_time']=df['drop_time'].astype(str)

X = df.drop(columns=["tripid", "label"])
X = X.fillna(X.mean())
y = df["label"].map({'incorrect': 0, 'correct': 1})
y = y.fillna(y.mean())
X_train, X_eval, y_train, y_eval = train_test_split(X,y,test_size=0.1,shuffle=True,stratify=y,random_state=RANDOM_SEED)

model = xgb.XGBClassifier(
 learning_rate =0.1,
 n_estimators=1000,
 colsample_bytree=0.8,
  max_depth=4,
 reg_alpha=0.005,
 min_child_weight=1,
 gamma=0,
 subsample=0.8,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)

numeric_cols = X.columns[X.dtypes != "object"].values
non_numeric_cols = X.columns[X.dtypes == 'object'].values

# chain preprocessing into a Pipeline object

numeric_preprocessing_steps = Pipeline(steps=[
    	('imputer', SimpleImputer(strategy='median')),
    	('scaler', StandardScaler())])

non_numeric_preprocessing_steps = Pipeline(steps=[
	('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
	('onehot', OneHotEncoder(handle_unknown='ignore'))])

preprocessor = ColumnTransformer(transformers = [("numeric", numeric_preprocessing_steps, numeric_cols),("non_numeric",non_numeric_preprocessing_steps,non_numeric_cols)],remainder = "drop")
full_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model),
])

full_pipeline.fit(X_train, y_train)

preds = full_pipeline.predict(X_eval)

print(accuracy_score(y_eval, preds))

print(classification_report(y_eval, preds))

print(f1_score(y_eval, preds, average='macro'))

test_fd = pd.read_csv("test.csv", index_col="tripid")

test_fd['drop_time'] = pd.to_datetime(test_fd.drop_time ,errors = "coerce")
test_fd['pickup_time'] = pd.to_datetime(test_fd.pickup_time ,errors = "coerce")

test_fd['calcu_duration'] = (test_fd.drop_time.dt.hour-test_fd.pickup_time.dt.hour)*3600 + (test_fd.drop_time.dt.minute-test_fd.pickup_time.dt.minute)*60

test_fd['pickup_time_hour'] = test_fd.pickup_time.dt.hour

test_fd['drop_time_hour'] =test_fd.drop_time.dt.hour

test_fd["distance"] =  distance(test_fd["pick_lat"],test_fd["pick_lon"],test_fd["drop_lat"],test_fd["drop_lon"])

test_fd['pickup_time']=test_fd['pickup_time'].astype(str)
test_fd['drop_time']=test_fd['drop_time'].astype(str)

test_probas=full_pipeline.predict(test_fd)
submission_df= pd.read_csv("sample_submission.csv", index_col="tripid")
print(submission_df.head())

submission_df["prediction"] = test_probas

print(submission_df.head())
submission_df.shape


from google.colab import  drive
drive.mount('/drive')

submission_df.to_csv('/drive/My Drive/ML/my_sub_8.csv', index=True)