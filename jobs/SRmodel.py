#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 14:59:41 2018

@author: markvonoven
"""

# XGBoost and TensorFlow packages
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Flatten, Conv2D
from tensorflow.python.keras.models import load_model
import numpy
import joblib
import time
import pandas as pd

#settings
start_time=time.time()
# fix random seed for reproducibility
numpy.random.seed(7)

#files
XG_filename = './SRmodels/finalized_XGmodel.sav'
K_filename = './SRmodels/Simple_Keras_model.h5'
FG_filename = './SRinput/current/future_games.csv'


def score_XGB(train_X, train_y, val_X, val_y):
    """
    Given properly split training data, this function creates and scores an XGBoost Classifier
    """
    XG_model = XGBClassifier()
    XG_model.fit(train_X, train_y)
    XG_preds = XG_model.predict(val_X)
    XG_scores = accuracy_score(val_y, XG_preds)
    
    # Print the scores for each model
    print('XG - Accuracy: ' + str(XG_scores))
    
def save_XGB(X, y):
    """
    Given a full training set (no splits), this function creates and saves a final model for predictions
    Intended to only be used after model has been properly scored with score_XGB
    """
    XG_final_model = XGBClassifier()
    XG_final_model.fit(X, y)
    joblib.dump(XG_final_model, XG_filename) 
    print('Final XG model trained and saved to ' + XG_filename)
    
def predict_XGB():
    """
    This function uses our saved XGB model and saved future schedule 
    to predict all remaining games for the current season
    """
    #read future games
    future_mstr = pd.read_csv(FG_filename)
    #extract features and prepare X for predictions
    features = future_mstr.columns[6:]
    X_new = future_mstr[features]
    #load saved model
    xgb = joblib.load(XG_filename)
    #make predictions
    XG_preds = xgb.predict(X_new)
    future_mstr['Predictions'] = XG_preds
    #return the relevant prediction information
    cols = ['Gamecode', 'Date', 'Team', 'Opp', 'Predictions']
    prediction_mstr_all = future_mstr[cols]
    
    return prediction_mstr_all
    
def score_Keras(X, y):
    """
    Given a full training set (no splits), this function creates and scores a Keras Classifer model
    """
    X_dim = X.shape[1]
    # create model
    model = Sequential()
    model.add(Dense(12, input_dim=X_dim, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model
    model.fit(X, y, epochs=150, batch_size=10)
    # evaluate the model
    scores = model.evaluate(X, y)
    print('150 epochs, 10 batch_size')
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    
    end_time=time.time()
    print("total time: ",end_time-start_time)
    
def scorensave_Keras(X, y):
    """
    Given a full training set (no splits), this function creates, scores
    and saves a Keras Classifer model for use in predictions
    NOTE:  Intended only for use after proper scoring of model using score_Keras (but not required)
    """
    X_dim = X.shape[1]
    # create model
    model = Sequential()
    model.add(Dense(12, input_dim=X_dim, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model
    model.fit(X, y, epochs=150, batch_size=10)
    # evaluate the model
    scores = model.evaluate(X, y)
    print('150 epochs, 10 batch_size')
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    
    end_time=time.time()
    print("total time: ",end_time-start_time)
    model.save(K_filename)
    print("Saved Keras model to " + K_filename)
    
def predict_Keras():
    """
    This function uses our saved Keras Classifier model and saved future schedule 
    to predict all remaining games for the current season
    """
    #read future games
    future_mstr = pd.read_csv(FG_filename)
    #extract features and prepare X for predictions
    features = future_mstr.columns[6:]
    X_new = future_mstr[features]
    #load saved model
    loaded_model = load_model(K_filename)
    # make predictions on the future games
    y_new = loaded_model.predict(X_new)
    # round predictions
    y_new = [round(x[0]) for x in y_new]
    # find prediction probabilities on the future games
    y_new_proba = loaded_model.predict_proba(X_new)
    # grab the future games and make a copy so you can add the predictions side by side
    prediction_mstr_w_preds = future_mstr.copy()
    # add the predictions and probabilities
    prediction_mstr_w_preds['Prediction'] = y_new
    prediction_mstr_w_preds['Proba'] = y_new_proba
    # keep only the columns you want to see
    cols = ['Gamecode', 'Date', 'Team', 'Opp', 'Prediction', 'Proba']
    prediction_final = prediction_mstr_w_preds[cols]
    
    return prediction_final
    