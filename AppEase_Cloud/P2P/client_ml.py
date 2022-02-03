# # Azure Machine Learning Classification client node
# - This script creates a client node to run the best performing model for predicting the labels (as identified in the 'AppEaseML.ipynb' notebook), and this script requires the output files of the 'AppEaseML.ipynb' notebook: 'train_data.csv', 'train_labels.csv', and 'best_model.pkl'.
# - This script should be run by calling "python3 client_ml.py".

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import pickle
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import urllib.request
import os


class Client(DatagramProtocol):
    def __init__(self, host, port):
        if host == "localhost":
            host = "127.0.0.1"
            
        self.id = host, port
        self.address = None
        self.server = '127.0.0.1', 9999
        print("Working on id:", self.id)
        
    def startProtocol(self):
        self.transport.write("ready".encode('utf-8'), self.server)
        
    def datagramReceived(self, datagram, addr):
        datagram = datagram.decode('utf-8')
        
        if addr == self.server:
            print("Choose a client from these\n", datagram)
            self.address = input("write host:"), int(input("write port:"))
            reactor.callInThread(self.send_message, 'This is the ML client')
        else:
            print(addr, ":", datagram)
            if datagram == 'Is the model ready?':
                try:
                    # Load model from file
                    model = pickle.load(open('best_model.pkl', 'rb'))

                    # load training data
                    train_data = pd.read_csv('train_data.csv')
                    train_labels = pd.read_csv('train_labels.csv')
                    reactor.callInThread(self.send_message('The model is ready'))
                except:
                    reactor.callInThread(self.send_message('The model is not ready'))
            elif datagram[0:4] == 'URL:':
                url = datagram[4:]
                urllib.request.urlretrieve(url, os.getcwd()+'/test_data.json')
                test_data = pd.read_json('test_data.json')
                
                # convert data types to int\n",
                test_data['bloodType'].replace(['A-','A+','B-','B+','AB-','AB+','O-','O+'], [0,1,2,3,4,5,6,7], inplace=True)
                test_data['sex'].replace(['Male','Female'],[0,1],inplace=True)
                test_data['name'] = test_data['name'].map(lambda x: int(x[4:]))
                test_data['TimeStamp'] = test_data['TimeStamp'].astype(int)
                
                model = pickle.load(open('best_model.pkl', 'rb'))
                train_data = pd.read_csv('train_data.csv')
                train_labels = pd.read_csv('train_labels.csv')
                
                # Calculate the accuracy score and predict target values
                ypred = model.fit(train_data,train_labels).predict(test_data)
                test_data['Predictions'] = ypred
                m = "Users classified as having a panic attack: "+", ".join([str(x) for x in sorted(test_data[test_data['Predictions']==1]['name'].unique())])
                reactor.callInThread(self.send_message, m)
            
    
    def send_message(self, message):
        self.transport.write(message.encode('utf-8'), self.address)
            
if __name__ == '__main__':
    port = randint(1000,5000)
    reactor.listenUDP(port, Client('127.0.0.1',port))
    reactor.run()
