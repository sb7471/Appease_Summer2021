#!/usr/bin/python

# btgui.py by Nadeem Abdul Hamid

"""
Module implementing simple BerryTella GUI for a simple p2p network.
"""


import sys
import threading

from random import *
from btfiler_specialized import *

import os
import tempfile


class AppEasePeer:
   def __init__( self, firstpeer, hops=2, maxpeers=5, serverport=5678, master=None, model=False ):
      self.btpeer = FilerPeer( maxpeers, serverport, model )

      host,port = firstpeer.split(':')
      self.init_hops = hops
      self.btpeer.buildpeers( host, int(port), hops=hops )
      self.host = host
      self.port = int(port)

      # Below is artifact of sample file sharing app built with btpeer.py
      #t = threading.Thread( target = self.btpeer.mainloop, args = [] )
      #t.start()
      
      #self.btpeer.startstabilizer( self.btpeer.checklivepeers, 3 )
      #self.btpeer.startstabilizer( self.onRefresh, 3 )
     
   def __onDestroy( self, event ):
      self.btpeer.shutdown = True

   def getPrimaryModelNode(self):
      """ Initiates the finding of the IP address and port for a single 
      modeling node in the network.

      Result:
      A tuple where the first element is a string equal to the IP address of 
      the identified modeling node and the second element is an int equal to 
      the port for the node.
      """
      for i in range(3):

         self.btpeer.buildpeers(self.host, self.port, hops=self.init_hops)

         result = self.btpeer.modelpeersearch(sys.maxsize)
         
         if result is None:
            # A reachable model peer was not found. Sleep and then check again
            # to see if a reachable model peer has entered the network.
            time.sleep(2)
            continue

         return result

   def find_model(self, intercept):
      """ Requests that a model is built using the data stored within the network
      and the specified modeling parameter.

      intercept (str):
         Specifies whether the fit_intercept parameter of the linear regression model
         being built should be set to True. Expected to be equal to "yes" if the
         fit_intercept parameter should be set to True.

      Returns:
      A str reporting performance metrics of the built model.
      """
      print('hello')
      result = self.getPrimaryModelNode()       
      data = self.btpeer.makerequest(result, intercept)
      data = ''.join(data).strip()
      print(data)
      return data

   def query_data(self, argument):
      """ Requests the query specified by argument to be run on the data stored
      on all modeling nodes contained within the network.

      argument (str):
         Specifies the parameters to use in querying the collected data and is 
         expected to contain a parameter (mean, median, mode, variance, stdev), 
         start date, and end data separated by commas.

      Returns:
      A str reporting the received query results.
      """
      result = self.getPrimaryModelNode()
      if result is not None:
         print("Sending request for query to", result, ":", argument)
         data = self.btpeer.submitquery(result, argument)
         data = ''.join(data).strip()
         #print(data)
         return data

   def visualize(self, argument):
      """ Requests that a visualization specified by argument is created using data
      stored on one modeling node.

      Parameters:
      argument (str):
         Specifies the visual to create and contains the name of a game and a feature 
         of recorded health data separated by a comma.

      Result:
      The bytes for the .png image of the created visual.
      """
      result = self.getPrimaryModelNode()
      if result is not None:
         print("Sending request for visualization", result, ":", argument)
         data = self.btpeer.submitvisrequest(result, argument)
         return data



def main():
   if len(sys.argv) < 4:
      print("Syntax: %s server-port max-peers peer-ip:port" % sys.argv[0])
      sys.exit(-1)

   serverport = int(sys.argv[1])
   maxpeers = sys.argv[2]
   peerid = sys.argv[3]
   app = AppEasePeer( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport )
   #app.find_model("no")
   #argument = ','.join(['stdev', '03-01-2021', '03-02-2021'])
   #app.query_data(argument)
   #argument = ','.join(['Angry-Birds','steps'])
   #app.visualize(argument)


# setup and run app
if __name__=='__main__':
   main()
