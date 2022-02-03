import os
import sys
import tempfile
import numpy as np
import pandas as pd
import texttoimage
import math
from ast import literal_eval as make_tuple
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from io import BytesIO
from .models import healthData
from django_pandas.io import read_frame
import datetime
from django.db.models import Q
import matplotlib.pyplot as plt
from pytz import timezone
import pytz

class Analytics:
    def predictUsingAzureML(self, data):
        return

    def visualize(self, game, feature):
    	param = ','.join([game, feature])
        # probably some sql code involved
    	visual_bytes = getDataFromDatabase(param)
    	visual_bytes = bytes.fromhex(visual_bytes)

    	fd, path = tempfile.mkstemp()
    	with open(path, 'wb') as file:
    		file.write(visual_bytes)

    	image = open(path, 'rb')
    	return FileResponse(image)

    def queryData(self, userToken, param, start, end):
        print('inside query_data')
        print(start)
        print(end)
        start = datetime.datetime.strptime(start, '%m-%d-%Y')
        end = datetime.datetime.strptime(end, '%m-%d-%Y')
        start = pytz.utc.localize(start)
        end = pytz.utc.localize(end)
        print(start, end)
        #qs = healthData.objects.filter(Q(timestamp__gt=start), Q(timestamp__lt=end),usertoken='taehyo97').values('timestamp','heartrate', 'stepscount', 'distancecovered')
        #fix datetime formatting in sql
        qs = healthData.objects.filter(usertoken=userToken).values('timestamp','heartrate', 'stepscount', 'distancecovered')
        #all_df_compressed = pd.DataFrame.from_records(qs)
        all_df_compressed = read_frame(qs)

        # filter out timestamps
        all_df_compressed['timestamp'] = pd.to_datetime(all_df_compressed['timestamp'])
        all_df_compressed = all_df_compressed[(all_df_compressed['timestamp'] > start) & (all_df_compressed['timestamp'] < end)]
        df = all_df_compressed.groupby(['timestamp']).sum()
        x = df.index.to_numpy()
        y1 = df['heartrate'].to_numpy()
        y2 = df['stepscount'].to_numpy()
        y3 = df['distancecovered'].to_numpy()

        #x_values = [datetime.datetime.strptime(d,"%m-%d-%Y").date() for d in df['timestamp']]
        if param == 'heartrate':
            plt.plot(x, y1, marker='+', markerfacecolor='skyblue', color='skyblue', label='heartrate')
        elif param == 'stepcount':
            plt.plot(x, y2, marker='.', markerfacecolor='green', color='green', label='stepscount')
        elif param == 'distance':
            plt.plot(x, y3, marker='1', markerfacecolor='orange', color='orange', label="distancecovered")
        elif param == 'all':
            plt.plot(x, y1, marker='+', markerfacecolor='skyblue', color='skyblue', label='heartrate')
            plt.plot(x, y2, marker='.', markerfacecolor='green', color='green', label='stepscount')
            plt.plot(x, y3, marker='1', markerfacecolor='orange', color='orange', label="distancecovered")

        # show legend
        plt.legend()

        # show graph
        plt.savefig("plot.png")
        plt.close()
        return

    def buildModel(self, userToken, intercept, start, end):
        print("Fetching data...")
        print(start, end)
        start = datetime.datetime.strptime(start, '%m-%d-%Y')
        end = datetime.datetime.strptime(end, '%m-%d-%Y')
        start = pytz.utc.localize(start)
        end = pytz.utc.localize(end)
        qs = healthData.objects.filter(usertoken=userToken).values('timestamp', 'heartrate', 'stepscount', 'distancecovered')
        #all_df_compressed = pd.DataFrame.from_records(qs)
        all_df_compressed = read_frame(qs)
        # filter out timestamps
        all_df_compressed['timestamp'] = pd.to_datetime(all_df_compressed['timestamp'])
        all_df_compressed = all_df_compressed[(all_df_compressed['timestamp'] > start) & (all_df_compressed['timestamp'] < end)]
        print(all_df_compressed)

        X = all_df_compressed[['stepscount','distancecovered']]
        Y = all_df_compressed['heartrate']

        x_train, x_test,y_train,y_test = train_test_split(X,Y,test_size =0.2)

        print("Training the model...")
        estimator = LinearRegression(fit_intercept = intercept)
        estimator.fit(x_train, y_train)

        # test model
        print("Evaluating the model...")
        y_predicted = estimator.predict(x_test)

        mae = metrics.mean_absolute_error(y_test, y_predicted)
        mse = metrics.mean_squared_error(y_test, y_predicted)
        r2 = metrics.r2_score(y_test, y_predicted)

        result = "Model results:\n Mean Absoluted Error:{},\nMean Square Error:{},\nR_Squared:{}".format(mae,mse,r2)
        print(result)
        return result
        # send back model and test result

        # TODO: Implement code to send actual model.
