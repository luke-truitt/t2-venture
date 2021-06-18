#%%
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
import os
import matplotlib.pyplot as plt
from numpy import array
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Bidirectional
from keras.layers import TimeDistributed
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.layers import Flatten
from keras.layers import ConvLSTM2D
import keras
import tensorflow as tf
import numpy as np
import sklearn
from sklearn import model_selection
from sklearn.metrics import mean_squared_error
#%%
dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(dir_path+"\\Street_Data_48209.txt", "r")
rawdict_of_street=f.read()
dict_of_street=json.loads(rawdict_of_street)
f.close()
#%%
list_of_values=[]
for i in dict_of_street.values():
    for j in i.values():
        ans=[]
        for k in j:
            ans.append(k['estimated_value_amount'])
        list_of_values.append(ans)
#%%
def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		end_ix = i + n_steps
		if end_ix > len(sequence)-1:
			break
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)
#%%
##Testing Vanilla LSTM on all data
n_steps=4
X_tot, y_tot=split_sequence(list_of_values[0],n_steps)
for i in range(1,len(list_of_values)):
    seq=list_of_values[i]
    X, y = split_sequence(seq, n_steps)
    try:
        X_tot=np.concatenate((X_tot, X),axis=0)
        y_tot=np.concatenate((y_tot, y))
    except ValueError:
        pass
#%%
n_features = 1
X_tot = X_tot.reshape((X_tot.shape[0], X_tot.shape[1], n_features))
#%%
model_single = Sequential()
model_single.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model_single.add(Dense(1))
model_single.compile(optimizer='adam', loss='mse')
#%%
X_train, X_test, y_train, y_test = model_selection.train_test_split(X_tot, y_tot, test_size=0.33)
#%%
model_single.fit(X_train, y_train, epochs=200, verbose=0)
#%%
yhat_single = model_single.predict(X_test, verbose=0)
yhat_single=yhat_single.reshape((yhat_single.shape[0],))
errors_single = mean_squared_error(y_test, yhat_single)
#print (errors_single)
#%%
#Stacked LSTM
n_features = 1
model_stack = Sequential()
model_stack.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps, n_features)))
model_stack.add(LSTM(50, activation='relu'))
model_stack.add(Dense(1))
model_stack.compile(optimizer='adam', loss='mse')
#%%
X_train, X_test, y_train, y_test = model_selection.train_test_split(X_tot, y_tot, test_size=0.33)
#%%
model_stack.fit(X_train, y_train, epochs=200, verbose=0)
#%%
yhat_stack = model_stack.predict(X_test, verbose=0)
yhat_stack=yhat_stack.reshape((yhat_stack.shape[0],))
errors_stack = mean_squared_error(y_test, yhat_stack)
#print (errors_stack)
#%%
model_bid = Sequential()
model_bid.add(Bidirectional(LSTM(50, activation='relu'), input_shape=(n_steps, n_features)))
model_bid.add(Dense(1))
model_bid.compile(optimizer='adam', loss='mse')
#%%
X_train, X_test, y_train, y_test = model_selection.train_test_split(X_tot, y_tot, test_size=0.33)
#%%
model_bid.fit(X_train, y_train, epochs=200, verbose=0)
#%%
yhat_bid = model_bid.predict(X_test, verbose=0)
yhat_bid = yhat_bid.reshape((yhat_bid.shape[0],))
errors_bid = mean_squared_error(y_test, yhat_bid)
#print (errors_bid)
#%%
n_steps=4
#CNN_LSTM
X_tot, y_tot=split_sequence(list_of_values[0],n_steps)
for i in range(1,len(list_of_values)):
    seq=list_of_values[i]
    X, y = split_sequence(seq, n_steps)
    try:
        X_tot=np.concatenate((X_tot, X),axis=0)
        y_tot=np.concatenate((y_tot, y))
    except ValueError:
        pass
n_features = 1
n_seq = 2
n_steps = 2
X_tot = X_tot.reshape((X_tot.shape[0], n_seq, n_steps, n_features))
model_cnn = Sequential()
model_cnn.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), input_shape=(None, n_steps, n_features)))
model_cnn.add(TimeDistributed(MaxPooling1D(pool_size=2)))
model_cnn.add(TimeDistributed(Flatten()))
model_cnn.add(LSTM(50, activation='relu'))
model_cnn.add(Dense(1))
model_cnn.compile(optimizer='adam', loss='mse')
#%%
X_train, X_test, y_train, y_test = model_selection.train_test_split(X_tot, y_tot, test_size=0.33)
model_cnn.fit(X_train, y_train, epochs=200, verbose=0)
yhat_cnn = model_cnn.predict(X_test, verbose=0)
yhat_cnn = yhat_cnn.reshape((yhat_cnn.shape[0],))
errors_cnn = mean_squared_error(y_test, yhat_cnn)
#print (errors_cnn)
#%%
#ConvLSTM
n_steps=4
X_tot, y_tot=split_sequence(list_of_values[0],n_steps)
for i in range(1,len(list_of_values)):
    seq=list_of_values[i]
    X, y = split_sequence(seq, n_steps)
    try:
        X_tot=np.concatenate((X_tot, X),axis=0)
        y_tot=np.concatenate((y_tot, y))
    except ValueError:
        pass
n_features = 1
n_seq = 2
n_steps = 2
X_tot=X_tot.reshape((X_tot.shape[0], n_seq, 1, n_steps, n_features))
model_conv = Sequential()
model_conv.add(ConvLSTM2D(filters=64, kernel_size=(1,2), activation='relu', input_shape=(n_seq, 1, n_steps, n_features)))
model_conv.add(Flatten())
model_conv.add(Dense(1))
model_conv.compile(optimizer='adam', loss='mse')
#%%
X_train, X_test, y_train, y_test = model_selection.train_test_split(X_tot, y_tot, test_size=0.33)
model_conv.fit(X_train, y_train, epochs=200, verbose=0)
yhat_conv = model_conv.predict(X_test, verbose=0)
yhat_conv = yhat_conv.reshape((yhat_cnn.shape[0],))
errors_conv = mean_squared_error(y_test, yhat_conv)
#print (errors_conv)
#%%
from math import sqrt
print (sqrt(errors_single))
print (sqrt(errors_stack))
print (sqrt(errors_bid))
print (sqrt(errors_cnn))
print (sqrt(errors_conv))
#%%