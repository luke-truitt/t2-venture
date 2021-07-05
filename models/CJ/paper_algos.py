import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.ensemble import GradientBoostingRegressor

# X = np.load('edited_X.npy')
# y = np.load('edited_y.npy')
X = []
y = []

# enumerated_y = {v: (k[0],k[1]) for v, k in enumerate(X)}
# print(enumerated_y)

zipcodes = []

with open('zipcodes.txt') as my_file:
    for line in my_file:
        if line[:-1] == "7875":
            zipcodes.append(line)
        else:
            zipcodes.append(line[:-1])

count = 0

# Removing the current zipcode from the file
for zipcode in zipcodes:
    pd_df = pd.read_pickle("paperfixed2019" + str(zipcode))

    # pd_df.head()
    # X.extend(pd_df.values[:,4:11]) 
    # y.extend(pd_df.values[:,-1])

    # continue

    sliced = pd_df.values[:,4:]

    # X.extend(sliced[:,:-1])

    for index in range(len(sliced)):
        x_value = (np.log(np.exp(sliced[index][-2])/(1+sliced[index][-1])))
        y_value = np.exp(sliced[index][-2])

        sliced[index][-2] = x_value
        sliced[index][-1] = y_value

    X.extend(sliced[:,:-1])
    y.extend(sliced[:,-1])

    # print(y)
    # pd_df.columns[4:]
    # print(len(pd_df))
    count += len(pd_df)

print(count)
print(np.array(X).shape)
print(np.array(y).shape)

# print(X)
# print(y)

# exit()

q=[0.021,0.979]
y_range = np.quantile(y,q)
print(y_range)

enumerated_y = {v:k for v, k in enumerate(y)}
# print(len(enumerated_y))
# should equal to be included?
enumerated_percentiles = {k: v for k, v in enumerated_y.items() if v >= y_range[0] and v <= y_range[1]}
# print(len(enumerated_percentiles))

X_edited = [X[i] for i in enumerated_percentiles.keys()]
y_edited = [i for i in enumerated_percentiles.values()]

# np.save("edited2_X", X)
# np.save("edited2_y", y)

# mean = np.mean(y)
# standard_deviation = np.std(y)
# distance_from_mean = abs(y - mean)
# max_deviations = 2
# not_outlier = distance_from_mean < max_deviations * standard_deviation
# no_outliers = y[not_outlier]
# print(max(no_outliers))

# q=[0.021,0.979]
# print(np.quantile(y,q))
# std = np.std(y)
# print(std)

# mean = np.mean(y)
# median = np.median(y)
# print(median)

# std_sum = 0
# for i in y:
#     std_sum += ((i - mean) ** 2)
# print(math.sqrt(std_sum/len(y)))

# y2 = sorted(i for i in y if i <= 12.15)
# print(len(y2))
# print(str(mean - 2 * std) + " " + str(mean - std) + " " + str(mean) + " " + str(mean + std) + " " + str(mean + 2 * std))
# print(max(y))
# print(min(y))

# X_train, X_test, y_train, y_test = train_test_split(
#     X_edited, y_edited, test_size=0.2, random_state=0)

# # MLR Model
# regr = linear_model.LinearRegression()
# regr.fit(X, y)

# Gradient Boosting Decision Trees Model
model = GradientBoostingRegressor()
# model = linear_model.LinearRegression()
# define the evaluation procedure
reg = model.fit(X_edited, y_edited)

# Back Test Set
first_count = 0
second_count = 0
X_test = []
y_test = []
appreciation_test = []
for zipcode in zipcodes:
    # print(zipcode)
    if zipcode == '78613':
        continue
    if zipcode == '78745':
        continue
    if zipcode == '78748':
        continue
    if zipcode == '78749':
        continue
    if zipcode == '78754':
        continue
    if zipcode == '78759':
        continue
    pd_df = pd.read_pickle("rawprice/paperrawpriceall" + str(zipcode))

    # pd_df.head()
    # X.extend(pd_df.values[:,4:11]) 
    # y.extend(pd_df.values[:,-1])

    # continue
    first_count += len(pd_df.values)
    sliced = [row for row in pd_df.values if row[1] != '2019-2014']
    second_count += len(sliced)
    # print(np.array(sliced).shape)

    sliced = np.array(sliced)[:,5:]

    # X.extend(sliced[:,:-1])

    X_test.extend(sliced[:,:-1])
    y_test.extend(sliced[:,-1])
    appreciation_test.extend([(row[-1] - np.exp(row[-2])) / np.exp(row[-2]) for row in sliced])

    # print(y)
    # pd_df.columns[4:]
    # print(len(pd_df))
    
print(first_count)
print(second_count)
print(np.array(X_test).shape)
print(np.array(y_test).shape)
# print(X_test[0])
# print(y_test[0])

# TEST QUANTILE SETUP
# IS THE APPRECIATION PERTCENTILE BETTER FOR CHECKING (OR EXCLUDE small changes !!!!!)
q=[0.021,0.979]
y_range = np.quantile(appreciation_test,q)
print(y_range)

enumerated_y = {v:k for v, k in enumerate(appreciation_test)}
enumerated_percentiles = {k: v for k, v in enumerated_y.items() if v >= y_range[0] and v <= y_range[1]}

X_test = [X_test[i] for i in enumerated_percentiles.keys()]
y_test = [y_test[i] for i in enumerated_percentiles.keys()]

print(np.array(X_test).shape)
print(np.array(y_test).shape)

print(reg.score(X_test, y_test))

cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
# evaluate the model
n_scores = cross_val_score(model, X, y, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
# report performance
print('MAE: %.3f (%.3f)' % (np.mean(n_scores), np.std(n_scores)))

# how should we build out the prediction pipeline
# check which data is best for training (use it all?)
# remember I'm treating demo house info as fixed (can safegraph help?)
# make it a classification problem