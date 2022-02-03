# AppEase Cloud Computing Project

Authors: Max Needle, Gautham Dinesh Kumar, Kiran Datti, Daksh Kumar

This repository contains the code for part 2 of our Cloud Computing Project, which migrated the AppEase system to the Azure cloud. The AppEase system was originally built by Nandhitha Raghuram, Nishchitha Prasad, and Vidit Bhargava for the NYU Rory Meyers College of Nursing. This system is meant to detect and respond to a person’s anxiety attacks. An Internet of Things (IoT) component of the application collects users’ health data from an iWatch (WatchOS) device connected to an iPhone (iOS) and then sends it to a web application managed on a Kafka server. Additionally, if an anxiety attack is detected, the web application can send notifications to the iWatch as well as options for relaxing games the user can play to calm their anxiety. For our portion of the project, we hoped to migrate this application to the Cloud to leverage its potential for cost savings, security, flexibility, mobility, and increased collaboration.

AppEase user health data and anxiety attack labels were simulated by running the 'simulate_data_and_labels.py' script. This data was uploaded to an Azure Storage Container through an Azure IoT Hub Device using the below '(RETIRED) AppEaseIoT.py' script. Automated machine learning (ML) analysis was run on the data to predict the simulated labels using the 'AppEaseML.ipynb' notebook. Finally, these IoT and ML cloud components were integrated into a peer-to-peer (P2P) messaging network to allow the simulated data to be quickly and automatically uploaded (IoT) and analyzed (ML).



1. 'simulate_data_and_labels.py'

This script creates simulated AppEase data in 2 JSON files ('simulated_health_data.json' for simulated user health data and 'random_labels.json' for simulated anxiety attack labels). This script should be run by calling "python3 create_data_and_labels.py [rows] [users]" where [rows] are the desired instances of collected data and [users] are the desired number of simulated users the data are collected from. The 'Sample Data' Folder contains an example of simulated data and labels for 100 instances of data for 5 distinct users. 
NOTE: At least 63 rows of data are required for Azure Machine Learning analytics (assuming a 0.8/0.2 train/test split).

2. '(RETIRED) AppEaseIoT.py'
**This script is not working!**
This script uploads a file as an Azure Storage Blob to a Container through an IoT Hub Device. This script requires an Azure IoT Hub that has been associated with a publicly-accessible Azure Storage Account Container and contains at least one IoT Device. This script should be run by calling "python3 AppEaseIoT.py [device_conn_str] [file]" where [device_conn_str] is the connection string of the IoT device created in the Azure IoT Hub and [file] is the name of the file in the local directory to be uploaded (i.e., 'simulated_health_data.json').

###### 2. (Tao Part) FileUpload.py:
Because the old script 'AppEaseIoT.py' was not working, I created a new script to upload files.
FileUpload.py
How to use the script: 
- CONNECTION_STRING: is the connection string of the IoT device created in the Azure IoT Hub
- PATH_TO_FILE = r"/Users/sabrinazhang/Documents/ITP/Appease_Summer2021/AppEase_Cloud/Sample_Data/random_labels.json"
*path_to_file is the path for the file in the local directory to be uploaded (i.e., 'simulated_health_data.json')*


3. 'AppEaseML.ipynb'

This notebook uses automated machine learning in Azure Machine Learning to create a classification model for predicting the above-created simulated labels (i.e., 'random_labels.json') from given data (i.e., 'simulated_health_data.json') and then outputs the best model ('best_model.pkl') and the data and labels used to train the best model (i.e., 'train_data.csv' and 'train_labels.csv'). The 'ML Analysis for Best Model' Folder contains examples of these output files. This notebook requires an Azure subscription. 
NOTE: It is recommended to run this notebook on an Azure Data Science Virtual Machine with a Python 3 kernel to ensure the necessary packages are installed.
**Comments by Tao**
- step0: create an Azure Data Science Virtual Machine
- step1: using x2goclient to connect the DSVM
- step2: run the notebook on the DSVM remotely, not locally. *you need using DSVM IP address to connect and run the notebook*

4. 'P2P' Folder

This folder contains the necessary files to create a peer-to-peer networking application for uploading and analyzing AppEase data against the previously-found best model. An IoT node uploads the data as a publicly-accessible Azure Storage Blob and then send the URL for the Blob to an ML client node, which loads the data and sends back a list of users which it predicts to be having an anxiety attack. A server node is first created by running "python3 server.py" before connecting the ML client node (creating by running "python3 client_ml.py") and the IoT client node (created by running "python3 client_iot.py [device_conn_str] [file]" where [device_conn_str] is the connection string of the IoT Device created in the Azure IoT Hub and [file] is the name of the file in the local directory to be uploaded). These Python scripts should also be run in a directory that contains the files outputed by the 'AppEaseML.ipynb' notebook (i.e., 'best_model.pkl', 'train_data.csv', and 'train_labels.csv'). Additionally, a 'client.py' script is included in this folder to showcase the messaging capabilities of this P2P network. By running 'python3 server.py' in one terminal window and then running 'python3 client.py' in another and then again running 'python3 client.py' in yet another terminal window, you can connect the two client nodes and send messages between them even after turning off the server node. 
