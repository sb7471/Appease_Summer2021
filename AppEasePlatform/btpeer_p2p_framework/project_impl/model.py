#!/usr/bin/python

# btgui.py by Nadeem Abdul Hamid

"""
Module implementing simple BerryTella GUI for a simple p2p network.
"""


import sys
import threading

from random import *
from btfiler_specialized import *


class AppEasePeer:
   def __init__( self, firstpeer, hops=2, maxpeers=5, serverport=5678, directory='../../data', 
      master=None, model=False):
      self.btpeer = FilerPeer( maxpeers, serverport, model, directory )

      host,port = firstpeer.split(':')
      self.btpeer.buildpeers( host, int(port), hops=hops )

      t = threading.Thread( target = self.btpeer.mainloop, args = [] )
      t.start()
      
      self.btpeer.startstabilizer( self.btpeer.checklivepeers, 3 )
#      self.btpeer.startstabilizer( self.onRefresh, 3 )
     

   def __onDestroy( self, event ):
      self.btpeer.shutdown = True
         


def main():
   if len(sys.argv) < 4:
      print("Syntax: %s server-port max-peers peer-ip:port (and optionally, data-directory)" % sys.argv[0])
      sys.exit(-1)

   serverport = int(sys.argv[1])
   maxpeers = sys.argv[2]
   peerid = sys.argv[3]

   if len(sys.argv) == 5:
      data_directory = sys.argv[4]
      app = AppEasePeer( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport, directory=data_directory, 
         model=True)
   else: 
      app = AppEasePeer( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport, model=True )


# setup and run app
if __name__=='__main__':
   main()
