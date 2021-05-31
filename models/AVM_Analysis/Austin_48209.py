#%%
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
import os
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
def tax_id_avm_input():
    Query_Input='''query MyQuery {
  usa_avm(where: {tax_assessor__tax_assessor_id: {_and: {fips_code: {_eq: "48209"}, city: {_eq: "AUSTIN"}}}}, distinct_on: tax_assessor_id) {
    tax_assessor__tax_assessor_id {
      address
      fips_code
      gross_sq_ft
      city
    }
    tax_assessor_id
    }
    }
    '''
    return Query_Input
#%%
QI=tax_id_avm_input()
OI="usa_avm"
data_diff_addr=make_query(QI, OI)
raw_diff_addr=json.dumps(data_diff_addr)
#%%
text_file = open("Full_Diff_48209.txt", "w")
n = text_file.write(raw_diff_addr)
text_file.close()
#%%