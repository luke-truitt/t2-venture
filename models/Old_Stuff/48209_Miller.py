#%%
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
import os
import matplotlib.pyplot as plt
#%%
logger = logging.getLogger(__name__)
#%%
url = 'https://graphql.cherre.com/graphql'
# Customize these variables.
file_dir = ''  # Must include trailing slash. If left blank, 
# csv will be created in the current directory.
api_email='lukeowentruitt@gmail.com'
api_token ='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJHcmFwaFFMIFRva2VuIiwibmFtZSI6IiIsImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ0Ml9kZXZlbG9wbWVudCJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLXVzZXItaWQiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLW9yZy1pZCI6InQyX2RldmVsb3BtZW50In19.sjHOw5oF3vYb3S_dxhWT7ucJ1qvQccDaHbyjzLkrKQQ'
api_account='Luke Truitt'
#%%
def get_graphql_request (Query):
    headers = {'content-type': 'application/json', 'X-Auth-Email': api_email, 'Authorization': api_token}
    # This variable replacement requires Python3.6 or higher
    payload = {"query": Query}
    r = requests.request("POST",url, json=payload, headers=headers)
    return r
#%%
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
#%%
def make_query(Query, obj):
    raw_data=get_graphql_request(Query)
    ans=serialize__to_json(raw_data, obj)
    return ans
#%%
dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(dir_path+"\\Ind_48209.txt", "r")
rawdict_of_timeseries=f.read()
dict_of_timeseries=json.loads(rawdict_of_timeseries)
f.close()
#%%
list_keys=list(dict_of_timeseries.keys())
#%%
street_keys=[]
for i in list_keys:
    starray=i.split(' ')
    starray=tuple(starray[1:])
    ans=' '.join(starray)
    street_keys.append(ans)
#%%
from collections import Counter
street_set=set(street_keys)
street_counter=Counter(street_keys)
#%%
def street_fn(string):
    starray=string.split(' ')
    starray=tuple(starray[1:])
    ans=' '.join(starray)
    return ans
#%%
miller_ln_keys=[]
for i in list_keys:
    if 'MILLER LN' in i:
        miller_ln_keys.append(i)
#%%
miller_ln_dod=dict()
for i in miller_ln_keys:
    miller_ln_dod[i]=dict_of_timeseries[i]
#%%
for i in miller_ln_dod.keys():
    miller_ln_dod[i]=sorted(miller_ln_dod[i], key=lambda i:i[
        'valuation_date'])
#%%
miller_dates=[]
miller_prices=[]
miller_houses=[]
for i in miller_ln_dod.keys():
    arr=[]
    parr=[]
    miller_houses.append(i)
    for j in miller_ln_dod[i]:
        arr.append(j['valuation_date'])
        parr.append(j['estimated_value_amount'])
    miller_dates.append(arr)
    miller_prices.append(parr)
#%%
miller_dataframes=[]
for i in range(5):
    ardf= pd.DataFrame({ 'dates' : miller_dates[i] , 'prices' : miller_prices[i] })
    miller_dataframes.append(ardf)
#%%
for i in range(5):
    plt.plot(miller_dates[i], miller_prices[i])
plt.legend(miller_houses)
plt.show()