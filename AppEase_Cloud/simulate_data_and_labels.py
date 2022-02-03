
# coding: utf-8

## AppEase Data and Label Simulation
# - This script outputs 'simulated_health_data.json' to the local directory, which contains the data fields outputed by AppEase's IoT component, but the health_data and user_data are merged.
# - This script outputs 'random_labels.json' to the local directory, which contains labels for whether the user was experiencing a panic attack (1) or not (0) at the time the data were collected.
# - This script should be run by called "python create_data_and_labels.py [rows] [users]" where [rows] are the desired instances of collected data and [users] are the desired number of simulated users the data are collected from.
# - NOTE: At least 63 rows of data are required for Azure Machine Learning analytics (assuming a 0.8/0.2 train/test split).


# import packages
import pandas as pd
import random
from datetime import datetime
import sys

# function to create simulated AppEase IoT dataset with x (int) rows and x (int) users and saving the data as 'simulated_health_data.json' and the label as 'random_labels.json' to the local directory
def simulate_data(rows, users):
    sata = pd.DataFrame(columns = [u'automotiveLabel',u'cyclingLabel', u'distance',u'heartRate',u'runningLabel', u'stationaryCount', u'stepCount',u'steps', u'unknownLabel', u'walkingLabel', u'age', u'bloodType',u'name', u'sex', u'TimeStamp']) # these are the data fields that would come from the AppEase IoT but the health_data and user_data are merged
    random_labels = pd.Series(name = 'Label', dtype = 'Int64') # initialize series with random labels
    
    for i in range(rows):
        year = random.randint(2014, 2022) # TimeStamp can be random
        month = random.randint(1, 12)
        day = random.randint(1,28)
        hour = random.randint(0,23)
        minute = random.randint(0,59)
        second = random.randint(0,59)
        TimeStamp = datetime(year, month=month, day=day, hour=hour, minute=minute, second=second)

        automotiveLabel = random.randint(0, 2) # other health data can also be random
        cyclingLabel = random.randint(0, 2)
        distance = random.randint(0, 50)
        heartRate = random.randint(0, 300)
        runningLabel = random.randint(0, 2)
        stationaryCount = random.randint(0, 2)
        stepCount = random.randint(0, 50)
        steps = random.randint(0, 50)
        unknownLabel = random.randint(0, 2)
        walkingLabel = random.randint(0, 2)
        
        user = random.randint(1,users) # user data has to stay constant for the user
        name = "User "+str(user)
        age = (user*user) % 150
        bloodType = ['A-','A+','B-','B+','AB-','AB+','O-','O+'][(user-1) % 8]
        sex = ['Male','Female'][(user-1) % 2]

        sata = sata.append({u'TimeStamp': TimeStamp, u'automotiveLabel':automotiveLabel, u'cyclingLabel':cyclingLabel, u'distance':distance,u'heartRate':heartRate, u'runningLabel':runningLabel,u'stationaryCount':stationaryCount, u'stepCount':stepCount,u'steps':steps, u'unknownLabel':unknownLabel, u'walkingLabel':walkingLabel, u'age':age, u'bloodType':bloodType,u'name':name, u'sex':sex}, ignore_index=True)
        
        # Random label of 1 or 0 for panic attack or not
        label =  random.randint(0, 1)
        random_labels = random_labels.append(pd.Series(label, name= 'Label'), ignore_index=True)
    
    # save simulated data to local directory
    sata.to_json('simulated_health_data.json')
    random_labels.to_json('random_labels.json')
    
# run above function to save simulated data and random labels JSON files to local file
simulate_data(int(sys.argv[1]), int(sys.argv[2]))
