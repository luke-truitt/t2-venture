import requests
import json
from itertools import chain
from collections import Counter
import pandas as pd
import numpy as np

headers = {"Content-Type": "application/json",
           "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJHcmFwaFFMIFRva2VuIiwibmFtZSI6IiIsImh0dHBzOi8vaGFzdXJhLmlvL2p3dC9jbGFpbXMiOnsieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ0Ml9kZXZlbG9wbWVudCJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLXVzZXItaWQiOiJ0Ml9kZXZlbG9wbWVudCIsIngtaGFzdXJhLW9yZy1pZCI6InQyX2RldmVsb3BtZW50In19.sjHOw5oF3vYb3S_dxhWT7ucJ1qvQccDaHbyjzLkrKQQ"}

# how to make the initial id accurate
prev = 0
counter = 0
units_left = True

loadedzipcode = 0
zipcodes = []

with open('zipcodes.txt') as my_file:
    for line in my_file:
        zipcodes.append(line)

if zipcodes[0][:-1] == "7875":
    # print('yes')
    # print(line)
    loadedzipcode = zipcodes[0]
else:
    # print('no')
    # print(line)
    loadedzipcode = zipcodes[0][:-1]

print(loadedzipcode)

# Removing the current zipcode from the file
if len(zipcodes) > 1:
    with open("zipcodes.txt", "w") as txt_file:
        for line in zipcodes[1:]:
            txt_file.write(line)

query = """query multipleFilters {
  tax_assessor(
    where: {_and: [{ mailing_zip: {_eq: "78617"} }, { property_use_standardized_code: {_eq: "385"} }, { tax_assessor_id: {_lt: 10000000000} }]}
    order_by: { tax_assessor_id: desc }
    limit: 100
  ) {
    tax_assessor_id
    mailing_address
    city
    mailing_zip
    latitude
    longitude
    year_built
    bed_count
    room_count
    bath_count
    stories_count
    building_sq_ft
    usa_zip_code_boundary__zip_code {
      usa_demographics__geography_id(order_by: { year: desc }) {
        year
        geography_type
        total_population_count
        average_household_income
        full_time_unemployed_count
        full_time_total_count
        race_white_count
        race_american_indian_count
        race_asian_count
        race_black_count
        race_hawaiian_count
        race_multiple_count
        race_hispanic_count
      }
    }
    usa_tax_assessor_history__tax_assessor_id(
      order_by: {assessed_year: desc}
    ) {
      assessed_year
      assessed_market_value_total
    }
  }
}"""

# do this on the tax_assessor object and only check the market value to see if you get more data
# break apart mailing address to verify it's processing correctly? is this needed?

#  address city zip


def check_cond(ob, ob_type):
    if ob_type == 'house':
        if ob['mailing_address'] is None:
            return False
        if ob['city'] is None:
            return False
        if ob['mailing_zip'] is None or ob['mailing_zip'] == 0 or ob['mailing_zip'] == "0":
            return False
        if ob['building_sq_ft'] is None or ob['building_sq_ft'] == 0:
            return False
        if ob['bed_count'] is None or ob['bed_count'] == 0:
            return False
        # is the second part necessary / does it need a third part
        if ob['latitude'] is None or ob['latitude'] == 0:
            return False
        if ob['longitude'] is None or ob['longitude'] == 0:
            return False
        # Studio SFR???
        if ob['bath_count'] is None or ob['bath_count'] == 0:
            return False
        if ob['year_built'] is None or ob['year_built'] == 0 or ob['year_built'] == "0":
            return False
        if ob['stories_count'] is None or ob['stories_count'] == 0:
            return False
    # or make it an if statement?
    elif ob_type == 'demo':
        # total_population_count
        # average_household_income
        # full_time_unemployed_count
        # full_time_total_count
        # race_white_count
        # race_american_indian_count
        # race_asian_count
        # race_black_count
        # race_hawaiian_count
        # race_multiple_count
        # race_hispanic_count
        if ob['year'] is None or ob['year'] == 0 or ob['year'] == "0":
            return False
        if ob['geography_type'] != 'ZI':
            return False
        # if ob['assessed_market_value_total'] is None or ob['assessed_market_value_total'] == 0:
        #     return False
    elif ob_type == 'assessment':
        if ob['assessed_year'] is None or ob['assessed_year'] == 0 or ob['assessed_year'] == "0":
            return False
        if ob['assessed_market_value_total'] is None or ob['assessed_market_value_total'] == 0:
            return False
    return True


url = 'https://graphql.cherre.com/graphql'

# CLEAR SOME OF THESE LISTS !!!!!
assessment_year_list = []
demo_year_list = []
df_info = []

# Do I need to account for the history array not existing


def data_experiments(json_data):
    # print(len(json_data['data']['tax_assessor']))
    for house in json_data['data']['tax_assessor']:
        assessment_years = []
        demo_years = []

        assessment_value_pairs = dict()
        demo_value_pairs = dict()
        # demo_2019 = {}

        if not check_cond(house, ob_type='house'):
            continue

        for assessment in house['usa_tax_assessor_history__tax_assessor_id']:
            if not check_cond(assessment, ob_type='assessment'):
                continue
            # print("passed 1")
            # print(assessment['assessed_year'])
            assessment_years.append(assessment['assessed_year'])
            assessment_value_pairs[assessment['assessed_year']
                                   ] = assessment['assessed_market_value_total']

        for demo in house['usa_zip_code_boundary__zip_code']["usa_demographics__geography_id"]:
            if not check_cond(demo, ob_type='demo'):
                continue
            # print('passed 2')
            demo_years.append(demo['year'])
            demo_value_pairs[demo['year']] = demo

            # if str(demo['year']) == '2019':
            #     demo_2019 = demo
        # print(assessment_years)
        assessment_res = [str(max(a, b)) + "-" + str(min(a, b))
                          for idx, a in enumerate(assessment_years) for b in assessment_years[idx + 1:] if a != b and abs(int(a)-int(b)) == 5]
        assessment_res = [x for x in assessment_res if x]
        assessment_year_list.append(assessment_res)
        demo_year_list.append(demo_years)
        
        # print(demo_year_list)
        # print(demo_years)=

        # print(demo_years)
        # print("Res: " + str(assessment_res))
        # !!!! Important to think about
        # Get 2014-2009 data (or really any year we can get an 5 year rate for) to predict if the appreciation rate is the same?
        # length shorter than 1 for each element, don't use it (assessment tears)
        # print("Assess")
        # print(assessment_res)
        # print(assessment_value_pairs.keys())
        for interval in assessment_res:
            basic_array = []
            # could reverse order and do insert at front within the statement to save time
            basic_array.append(house['tax_assessor_id'])
            basic_array.append(interval)
            basic_array.append(house['mailing_address'])
            basic_array.append(house['city'])
            basic_array.append(house['mailing_zip'])

            basic_array.append(house['latitude'])
            basic_array.append(house['longitude'])
            basic_array.append(house['bath_count'])
            basic_array.append(house['bed_count'])
            basic_array.append(house['year_built'])
            basic_array.append(house['stories_count'])
            basic_array.append(house['building_sq_ft'])
            high = int(interval.split('-')[0])
            low = interval.split('-')[1]
            # print(type(high))
            # print(type(demo_years[0]))
            if high in demo_years:
                # print(demo_years)
                # print(demo_value_pairs.keys())
                # print("YES: " + str(high))
                # print(demo_value_pairs)
                house_array = basic_array
                #'White Count', 'White Ratio', 'Native Count', 'Native Ratio', 'Asian Count', 'Asian Ratio', 'Black Count', 'Black Ratio',
                house_array.append(demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['average_household_income'])
                house_array.append(
                    demo_value_pairs[high]['full_time_unemployed_count'] / demo_value_pairs[high]['full_time_total_count'])
                house_array.append(demo_value_pairs[high]['race_white_count'])
                house_array.append(
                    demo_value_pairs[high]['race_white_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_american_indian_count'])
                house_array.append(
                    demo_value_pairs[high]['race_american_indian_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_asian_count'])
                house_array.append(
                    demo_value_pairs[high]['race_asian_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_black_count'])
                house_array.append(
                    demo_value_pairs[high]['race_black_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_hawaiian_count'])
                house_array.append(
                    demo_value_pairs[high]['race_hawaiian_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_multiple_count'])
                house_array.append(
                    demo_value_pairs[high]['race_multiple_count']/demo_value_pairs[high]['total_population_count'])
                house_array.append(demo_value_pairs[high]['race_hispanic_count'])
                house_array.append(
                    demo_value_pairs[high]['race_hispanic_count']/demo_value_pairs[high]['total_population_count'])

                # this is adjusted for predicting the raw 2019 price
                # !!! DOES THE STRING CASTING NEED TO WORK
                house_array.append(np.log(assessment_value_pairs[str(low)]))
                house_array.append(assessment_value_pairs[str(high)])
                # house_array.append(
                #     (assessment_value_pairs['2019'] - assessment_value_pairs['2014']) / assessment_value_pairs['2014'])

                # print("House Array: " + str(len(house_array)))
                df_info.append(house_array)

        # if len(years) > 0:
        #     print(house)


# {{ tax_assessor_id: {{ _lt: {previous_id} }} }}{{ tax_assessor_id: {{ _lt: {previous_id} }} }}
while units_left:
    if counter != 0:

        # print(loadedzipcode)

        query = """query multipleFilters {{
        tax_assessor(
            where: {{ _and: [ {{ mailing_zip: {{_eq: "{zipcode}" }} }}, {{ property_use_standardized_code: {{_eq: "385"}} }}, {{ tax_assessor_id: {{_lt: {previous_id} }} }} ] }}
            order_by: {{ tax_assessor_id: desc }}
            limit: 100
        ) {{
            tax_assessor_id
            mailing_address
            city
            mailing_zip
            latitude
            longitude
            year_built
            bed_count
            room_count
            bath_count
            stories_count
            building_sq_ft
            usa_zip_code_boundary__zip_code {{
            usa_demographics__geography_id(order_by: {{ year: desc }}) {{
                year
                geography_type
                total_population_count
                average_household_income
                full_time_unemployed_count
                full_time_total_count
                race_white_count
                race_american_indian_count
                race_asian_count
                race_black_count
                race_hawaiian_count
                race_multiple_count
                race_hispanic_count
              }}
            }}
            usa_tax_assessor_history__tax_assessor_id(
            order_by: {{ assessed_year: desc }}
            ) {{
                assessed_year
                assessed_market_value_total
            }}
          }}
        }}""".format(previous_id=str(prev), zipcode=str(loadedzipcode))

    r = requests.post(url, json={'query': query}, headers=headers)
    # print(r.status_code)
    # print(r.text)

    # TEMP
    # zip_index += 1
    # prev = 10000000000
    # continue

    json_data = json.loads(r.text)
    # print(query)
    # print(json_data)
    # print(json_data)
    # print(len(json_data['data']['tax_assessor']))

    # get_df_info(json_data)
    data_experiments(json_data)
    # print("DF INFO: " + str(len(df_info)))

    # print(json_data['data']['tax_assessor'])
    # print(len(json_data['data']['tax_assessor']))

    # last_unit = json_data['data']['tax_assessor'][-1]

    # file1.write("ID: " + str(last_unit['tax_assessor_id']) + "\n" + "Address: " + str(
    #     last_unit['mailing_address']) + "\n" + str(len(json_data['data']['tax_assessor'])) + "\n")

    if len(json_data['data']['tax_assessor']) < 100:
        # did this cause problems in the previous method?
        prev = 10000000000

        # Print this each time?
        print(len(assessment_year_list))
        flatten_list_1 = list(chain.from_iterable(assessment_year_list))
        print(Counter(flatten_list_1))

        print(len(demo_year_list))
        flatten_list_2 = list(chain.from_iterable(demo_year_list))
        print(Counter(flatten_list_2))

        file1 = open(str(loadedzipcode) + ".txt", "w")
        file1.write(str(loadedzipcode) + "\n")
        file1.write(str(flatten_list_1) + "\n")
        file1.write(str(flatten_list_2) + "\n")
        file1.close()

        # year_list = []

        print(df_info)
        # !!!!!!!!!!!!!!!!!!
        # Why does using price make sense? cuz when predicting that assumes you have a forecast which defeats the purpose? or is it just to predict a continuous appreciate rate over any 5 year interval?
        df = pd.DataFrame(df_info, columns=['Assessor ID', 'Interval', 'Address', 'City', 'Zipcode', 'Latitude', 'Longitude', 'Baths', 'Beds',
                          'Built Year', 'Floors', 'Square Footage', 'Population', 'Average House Income', 'Unemployment Rate', 'White Count', 'White Ratio', 'Native Count', 'Native Ratio', 'Asian Count', 'Asian Ratio', 'Black Count', 'Black Ratio', 'Hawaiian Count', 'Hawaiian Ratio', 'Multiple Count', 'Multiple Ratio', 'Hispanic Count', 'Hispanic Ratio', 'Log Original Price', '5 Year Price'])
        print(df.head)

        df.to_pickle("rawprice/paperrawpriceall" + str(loadedzipcode))

        # print(np.array(df_info).shape)
        # X = np.array(df_info)[:, :-1]
        # print(X.shape)
        # y = np.array(df_info)[:, -1]
        # print(y.shape)
        # np.save(str(loadedzipcode) + "_X", X)
        # np.save(str(loadedzipcode) + "_y", y)

        # zip_index += 1

        # df_info = []

        units_left = False

    prev = json_data['data']['tax_assessor'][-1]['tax_assessor_id']
    counter += 1
    print(counter)

# print(len(year_list))
# flatten_list = list(chain.from_iterable(year_list))
# print(Counter(flatten_list))

# # file1.close()
# # print(np.array(df_info).shape)
# # TAKE ONLY THE 9 YEAR EXAMPLES
# # df_info = [x for x in df_info if x[1] == 9]
# # print(len(df_info))

# X = np.array(df_info)[:, :-1]
# print(X.shape)
# y = np.array(df_info)[:, -1]
# print(y.shape)
# np.save("X", X)
# np.save("y", y)

# df = pd.DataFrame(df_info, columns=['Latitude',
#                                     'Longitude', 'Baths', 'Beds', 'Built Year', 'Floors', 'Square Footage', 'Appreciation Rate'])
# # print(df.head)
# # print(df['Years'].value_counts())
# df.to_pickle("austinzips")
