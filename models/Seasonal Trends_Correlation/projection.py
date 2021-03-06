# -*- coding: utf-8 -*-
"""Projection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CpxkDtt5YI0Dn_wVgcSXbut1qk4yB4sO
"""

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
import math

logger = logging.getLogger(__name__)

url = 'https://graphql.cherre.com/graphql'
# Customize these variables.
file_dir = ''  # Must include trailing slash. If left blank, 
# csv will be created in the current directory.
api_email='lukeowentruitt@gmail.com'
api_token ='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJHcmFwaFFMIFRva2VuIiwibmFtZSI6IiIsImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ0Ml9kZXZlbG9wbWVudCJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLXVzZXItaWQiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLW9yZy1pZCI6InQyX2RldmVsb3BtZW50In19.sjHOw5oF3vYb3S_dxhWT7ucJ1qvQccDaHbyjzLkrKQQ'
api_account='Luke Truitt'

def get_graphql_request (Query):
    headers = {'content-type': 'application/json', 'X-Auth-Email': api_email, 'Authorization': api_token}
    # This variable replacement requires Python3.6 or higher
    payload = {"query": Query}
    r = requests.request("POST",url, json=payload, headers=headers)
    return r

def get_graphql_request_variables (Query,Variables):
    headers = {'content-type': 'application/json', 'X-Auth-Email': api_email, 'Authorization': api_token}
    # This variable replacement requires Python3.6 or higher
    payload = {"query": Query, "variables": Variables}
    r = requests.request("POST",url, json=payload, headers=headers)
    return r

def serialize__to_json(cherre, obj):
    """
    Function converts cherre API response to reduced dictionary"""
    if not (isinstance(cherre, requests.models.Response)):
        raise TypeError(
            f"The cherre must be a requests.models.Response, found {type(cherre)}."
        )
    elif not (isinstance(obj, str)):
        raise TypeError(f"The object you are querying must be a str, found {type(obj)}.")
    else:
        if cherre.status_code == 200:
            json_response = json.loads(cherre.content)
            try:
                hits = json_response.get("data").get(obj)
            except AttributeError:
                logger.info(f"No hits found under multimatch for this object query for {obj}.")
                hits = 0
            return hits

def make_eval_df(y_pred,y_true, date):
    y_pred.name='y_pred'
    y_true.name='y_true'
    date.name='date'
    df = pd.concat([y_pred,y_true,date],axis=1)
    for i, row in df.iterrows():
      if i==0:
        df.at[i, 'move_pred']=np.nan
        df.at[i, 'move_true']=np.nan
      else:
        df.at[i, 'move_pred']=df['y_pred'][i]-df['y_pred'][i-1]
        df.at[i, 'move_true']=df['y_true'][i]-df['y_true'][i-1]
    #move_pred.name='move_pred'
    #move_true.name='move_true'
    df['sign_pred'] = df.move_pred.apply(np.sign)
    df['sign_true'] = df.move_true.apply(np.sign)
    df['is_correct'] = 0
    df.loc[df.sign_pred * df.sign_true > 0 ,'is_correct'] = 1 
    df['is_incorrect'] = 0
    df.loc[df.sign_pred * df.sign_true < 0,'is_incorrect'] = 1 
    df['is_predicted'] = df.is_correct + df.is_incorrect
    df['result'] = df.sign_pred * df.move_true
    return df

def calc_scorecard(df):
    scorecard = pd.Series(dtype='float64')
    # building block metrics
    scorecard.loc['accuracy'] = df.is_correct.sum()*1. / (df.is_predicted.sum()*1.)*100
    scorecard.loc['edge'] = df.result.mean()
    scorecard.loc['noise'] = df.move_pred.diff().abs().mean()
    scorecard.loc['move_true_chg'] = df.move_true.abs().mean()
    scorecard.loc['move_pred_chg'] = df.move_pred.abs().mean()
    scorecard.loc['prediction_calibration'] = scorecard.loc['move_pred_chg']/scorecard.loc['move_true_chg']
    scorecard.loc['capture_ratio'] = scorecard.loc['edge']/scorecard.loc['move_true_chg']*100
    scorecard.loc['edge_long'] = df[df.sign_pred == 1].result.mean()  - df.move_true.mean()
    scorecard.loc['edge_short'] = df[df.sign_pred == -1].result.mean()  - df.move_true.mean()
    scorecard.loc['edge_win'] = df[df.is_correct == 1].result.mean()  - df.move_true.mean()
    scorecard.loc['edge_lose'] = df[df.is_incorrect == 1].result.mean()  - df.move_true.mean()
    return scorecard

def make_query(Query, obj):
    raw_data=get_graphql_request(Query)
    ans=serialize__to_json(raw_data, obj)
    return ans

def make_query_variables(Query, Variables, obj):
    raw_data=get_graphql_request_variables(Query, Variables)
    ans=serialize__to_json(raw_data, obj)
    return ans

def neighborhood_list_query_asc_48209_austin():
    QI='''query MyQuery($previous_id: numeric!) {
    usa_avm(where: {tax_assessor__tax_assessor_id: {_and: {fips_code: {_eq: "48209"}, city: {_eq: "AUSTIN"}, tax_assessor_id: {_gt: $previous_id}}}}, distinct_on: tax_assessor_id, order_by: {tax_assessor_id: asc}, limit: 100) {
    tax_assessor_id
    tax_assessor__tax_assessor_id {
      parcel_boundary__tax_assessor_id {
        fips_code
      }
      tax_assessor_usa_neighborhood_boundary__bridge {
        usa_neighborhood_boundary__geography_id {
          geography_id
          geography_code
          boundary_id
          area
        }
      }
      address
    }
    }
    }'''
    return QI

data_diff_demog=[]
#Non-Empty Initialization
last_id=1544919
while (1):
  QI=neighborhood_list_query_asc_48209_austin()
  VI={"previous_id":last_id}
  OI="usa_avm"
  data_diff=make_query_variables(QI, VI, OI)
  if (not data_diff):
    break
  data_diff_demog=data_diff_demog+data_diff
  last_id=data_diff[len(data_diff)-1]['tax_assessor_id']

def geography_id_list_48209():
  QI='''query MyQuery($prev_geography_id: String!) {
  usa_demographics(where: {_and: {county_code_5: {_eq: "48209"}, geography_id: {_gt: $prev_geography_id}}}, distinct_on: geography_id, order_by: {geography_id: asc}) {
    geography_id
    geography_code
    geography_name
  }
  }'''
  return QI

#Non-Empty Initialization
last_geog_id="C048208"
data_geog_demog=[]
while (1):
  QI=geography_id_list_48209()
  VI={"prev_geography_id": last_geog_id}
  OI="usa_demographics"
  data_geog=make_query_variables(QI, VI, OI)
  if (not data_geog):
    break
  data_geog_demog=data_geog_demog+data_geog
  last_geog_id=data_geog[len(data_geog)-1]['geography_id']

def census_geog_query(id):
  QI='''query MyQuery {
  usa_demographics(where: {geography_id: {_eq: "'''+id+'''"}}) {
    year
    age_ave_projected_10_year
    age_ave_projected_5_year
    airport_distance
    closest_major_city
    education_graduate_degree_count
    education_high_school_graduate_count
    education_less_than_9_count
    education_some_college_count
    education_some_high_school_count
    education_total_population_count
    median_household_income_25_44
    median_household_income_45_64
    median_household_income_5_year_forecast
    median_household_income_over_65
    median_household_income_under_25
    population_2000_count
    population_2010_count
    population_5_year_forecast
    population_5_year_forecast_high
    population_5_year_forecast_low
    population_age_00_04_count
    population_age_05_09_count
    population_age_10_14_count
    population_age_15_19_count
    population_age_20_24_count
    population_age_25_29_count
    population_age_30_34_count
    population_age_35_39_count
    population_age_40_44_count
    population_age_45_49_count
    population_age_50_54_count
    population_age_55_59_count
    population_age_60_64_count
    population_age_65_69_count
    population_age_70_74_count
    population_age_75_79_count
    population_age_80_84_count
    population_age_over_85_count
    population_density
    population_diff_2000_percent
    population_diff_2010_percent
    race_asian_2000_count
    race_asian_count
    race_asian_projected_5_year_count
    race_black_2000_count
    race_black_count
    race_black_projected_5_year_count
    race_hispanic_count
    race_hispanic_projected_5_year_count
    race_other_count
    race_other_projected_5_year_count
    race_total_population_count
    race_white_2000_count
    race_white_count
    race_white_projected_5_year_count
  }
  }'''
  return QI

Obj_Input="usa_demographics"
dict_of_demog=dict()
for i in data_geog_demog:
  gid=i['geography_id']
  js_output=make_query(census_geog_query(gid),Obj_Input)
  dict_of_demog[gid]=js_output

def time_series_query(address_input):
    QI='''query MyQuery {
    usa_avm(where: {tax_assessor__tax_assessor_id: {_and: {city: {_eq: "AUSTIN"}, address: {_eq: "'''+address_input+'''"}}}}) {
    estimated_max_value_amount
    estimated_min_value_amount
    estimated_value_amount
    valuation_date
    tax_assessor__tax_assessor_id {
      address
      fips_code
      gross_sq_ft
      city
    }
    tax_assessor_id
    }
    }'''
    return QI

Obj_Input="usa_avm"

dict_of_48209_ind=dict()
for i in range(len(data_diff_demog)):
    ad_input=data_diff_demog[i]['tax_assessor__tax_assessor_id']['address']
    js_output=make_query(time_series_query(ad_input), Obj_Input)
    dict_of_48209_ind[ad_input]=js_output
    dict_of_48209_ind[ad_input]=sorted(dict_of_48209_ind[ad_input], key=lambda x:x ['valuation_date'])

len(dict_of_48209_ind.keys())

arr=[]
for i in dict_of_48209_ind.keys():
  arr.append(len(dict_of_48209_ind[i]))
import collections
print (collections.Counter(arr))

dict_of_34=dict()
for i in dict_of_48209_ind.keys():
  if len(dict_of_48209_ind[i])==34:
    dict_of_34[i]=dict_of_48209_ind[i]

arr_of_arr_of_dates=[]
for i in dict_of_48209_ind.keys():
  if len(dict_of_48209_ind[i])==34:
    foo=[]
    for j in range(34):
      foo.append(dict_of_48209_ind[i][j]['valuation_date'])
    arr_of_arr_of_dates.append(foo)

flag=True
for i in range(2748):
  if arr_of_arr_of_dates[i]!=arr_of_arr_of_dates[0]:
    flag=False
    break
print (flag)
###The 2748 houses with 34 valuations are homogenous!

list_of_full_dates=arr_of_arr_of_dates[0]
list_of_train_dates=[]
list_of_test_dates=[]
for i in list_of_full_dates:
  if '2018' in i or '2019' in i:
    list_of_train_dates.append(i)
  elif '2020' in i or '2021' in i:
    list_of_test_dates.append(i)

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

#data_diff_demog and dict_of_48209_ind have different lengths, so examine
A=set(dict_of_48209_ind.keys())
B=set()
for i in data_diff_demog:
  x=i['tax_assessor__tax_assessor_id']['address']
  B.add(x)
#Turns out that same home with same address has had multiple owners, hence the new tax_assessor_id

time_period={'2018-01-22':1, '2018-02-22':2, '2018-03-23':3, '2018-04-20':4, '2018-05-25':5, '2018-06-25':6, '2018-07-20':7,
             '2018-08-20':8, '2018-09-19':9, '2018-10-23':10, '2018-11-20':11, '2018-12-21':12, '2019-06-21':18, '2019-07-25':19,
             '2019-08-22':20, '2019-09-23':21, '2019-10-22':22, '2019-11-22':23, '2019-12-27':24, '2020-01-22':25, '2020-02-20':26,
             '2020-03-20':27, '2020-04-24':28, '2020-05-22':29, '2020-06-19':30, '2020-07-24':31, '2020-08-21':32, '2020-09-21':33,
             '2020-10-23':34, '2020-11-20':35, '2020-12-24':36, '2021-02-09':38, '2021-03-12':39, '2021-04-09':40}

dict_of_values=dict()
for i in dict_of_34.keys():
    dict_of_values[i]=dict()
    for j in dict_of_34[i]:
        dict_of_values[i][time_period[j['valuation_date']]]=[j['estimated_max_value_amount'],j['estimated_min_value_amount'],j['estimated_value_amount']]

list_max_med_ratio=[]
list_min_med_ratio=[]
for i in dict_of_values.keys():
  for j in dict_of_values[i].values():
    list_max_med_ratio.append(j[0]/j[2])
    list_min_med_ratio.append(j[1]/j[2])

import matplotlib.pyplot as plt
plt.scatter(list_max_med_ratio, list_min_med_ratio)
#Roughly symmetric about y=-x axis

for i in dict_of_values.keys():
  dict_of_values[i][13]=[(dict_of_values[i][12][0]*5+dict_of_values[i][18][0]*1)/6, (dict_of_values[i][12][1]*5+dict_of_values[i][18][1]*1)/6, (dict_of_values[i][12][2]*5+dict_of_values[i][18][2]*1)/6]
  dict_of_values[i][14]=[(dict_of_values[i][12][0]*4+dict_of_values[i][18][0]*2)/6, (dict_of_values[i][12][1]*4+dict_of_values[i][18][1]*2)/6, (dict_of_values[i][12][2]*4+dict_of_values[i][18][2]*2)/6]
  dict_of_values[i][15]=[(dict_of_values[i][12][0]*3+dict_of_values[i][18][0]*3)/6, (dict_of_values[i][12][1]*3+dict_of_values[i][18][1]*3)/6, (dict_of_values[i][12][2]*3+dict_of_values[i][18][2]*3)/6]
  dict_of_values[i][16]=[(dict_of_values[i][12][0]*2+dict_of_values[i][18][0]*4)/6, (dict_of_values[i][12][1]*2+dict_of_values[i][18][1]*4)/6, (dict_of_values[i][12][2]*2+dict_of_values[i][18][2]*4)/6]
  dict_of_values[i][17]=[(dict_of_values[i][12][0]*1+dict_of_values[i][18][0]*5)/6, (dict_of_values[i][12][1]*1+dict_of_values[i][18][1]*5)/6, (dict_of_values[i][12][2]*1+dict_of_values[i][18][2]*5)/6]
  dict_of_values[i][37]=[(dict_of_values[i][36][0]+dict_of_values[i][38][0])/2, (dict_of_values[i][36][1]+dict_of_values[i][38][1])/2, (dict_of_values[i][36][2]+dict_of_values[i][38][2])/2]

train_list_of_med_val=[]
train_list_of_max_val=[]
train_list_of_min_val=[]
for i in dict_of_values.values():
  med=[]
  min=[]
  max=[]
  for j in range(1,25):
    med.append(i[j][2])
    min.append(i[j][1])
    max.append(i[j][0])
  train_list_of_med_val.append(med)
  train_list_of_max_val.append(max)
  train_list_of_min_val.append(min)

test_list_of_med_val=[]
test_list_of_max_val=[]
test_list_of_min_val=[]
for i in dict_of_values.values():
  med=[]
  min=[]
  max=[]
  for j in range(26,41):
    med.append(i[j][2])
    min.append(i[j][1])
    max.append(i[j][0])
  test_list_of_med_val.append(med)
  test_list_of_max_val.append(max)
  test_list_of_min_val.append(min)

def preprocess_sequence(arr, n_steps=4):
  X_tot, y_tot=split_sequence(arr[0],n_steps)
  for i in range(1,len(arr)):
    X, y = split_sequence(arr[i], n_steps)
    X_tot=np.concatenate((X_tot, X),axis=0)
    y_tot=np.concatenate((y_tot, y))
    return X_tot, y_tot

X_train_med, y_train_med=preprocess_sequence(train_list_of_med_val)
X_train_max, y_train_max=preprocess_sequence(train_list_of_max_val)
X_train_min, y_train_min=preprocess_sequence(train_list_of_min_val)

X_test_med, y_test_med=preprocess_sequence(test_list_of_med_val)
X_test_max, y_test_max=preprocess_sequence(test_list_of_max_val)
X_test_min, y_test_min=preprocess_sequence(test_list_of_min_val)

#ALWAYS RUN THIS BEFORE TESTING A NEW MODEL

n_features = 1
n_steps=4

X_train_med = X_train_med.reshape((X_train_med.shape[0], X_train_med.shape[1], n_features))
X_train_max = X_train_max.reshape((X_train_max.shape[0], X_train_max.shape[1], n_features))
X_train_min = X_train_min.reshape((X_train_min.shape[0], X_train_min.shape[1], n_features))

model_single_1 = Sequential()
model_single_1.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model_single_1.add(Dense(1))
model_single_1.compile(optimizer='adam', loss='mse')
model_single_1.fit(X_train_med, y_train_med, epochs=200, verbose=0)

model_single_2 = Sequential()
model_single_2.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model_single_2.add(Dense(1))
model_single_2.compile(optimizer='adam', loss='mse')
model_single_2.fit(X_train_max, y_train_max, epochs=200, verbose=0)

model_single_3 = Sequential()
model_single_3.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model_single_3.add(Dense(1))
model_single_3.compile(optimizer='adam', loss='mse')
model_single_3.fit(X_train_min, y_train_min, epochs=200, verbose=0)

import seaborn as sns

from statsmodels.tsa.stattools import adfuller

train_df_med=pd.DataFrame(train_list_of_med_val, columns=[i for i in range(1,25)])
train_df_max=pd.DataFrame(train_list_of_max_val, columns=[i for i in range(1,25)])
train_df_min=pd.DataFrame(train_list_of_min_val, columns=[i for i in range(1,25)])

autocorr=dict()
for j in range(1,13):
  ans=0
  for i in train_list_of_med_val:
    df=pd.DataFrame(i)
    ans=ans+df[0].autocorr(lag=j)
  ans=ans/len(train_list_of_med_val)
  autocorr[j]=ans

autocorr

from statsmodels.tsa.seasonal import seasonal_decompose