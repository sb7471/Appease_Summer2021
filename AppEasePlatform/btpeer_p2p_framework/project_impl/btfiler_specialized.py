#!/usr/bin/python

# The following methods are thanks to Nadeem Abdul Hamid
# (http://cs.berry.edu/~nhamid/p2p/filer-python.html): __router,
# __handle_insertpeer, __handle_listpeers, __handle_peername,
# __handle_query, __handle_quit, buildpeers

from btpeer import *
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
from sklearn import metrics
from io import BytesIO

sys.path.insert(1, '../../data') or sys.path.insert(1, '../data')
from visualize import Visualize
from filter import Filter
from quickQuery import QuickQuery

PEERNAME = "NAME"	 # request a peer's canonical id
LISTPEERS = "LIST"
INSERTPEER = "JOIN"
QUERY = "QUER"
FILEGET = "FGET"
PEERQUIT = "QUIT"
REPLY = "REPL"
ERROR = "ERRO"

# RC CHANGE
MODEL = "MODL" # request id's of modelling peers only
FILESEND = "FSEN"
QUERYSEND = "QSEN"
QUERYREQ = "QUER"
VISREQ = "VISR"

# EVA CHANGE
DATAQUERY = "DATQ" # used to query data on a peer without downloading it
BUILDMODEL = "BMOD"

# DATA_DIR = 'Spring21_SE_project/data'

# Assumption in this program:
#	 peer id's in this application are just "host:port" strings

#==============================================================================
class FilerPeer(BTPeer):
#==============================================================================
	""" Implements a file-sharing peer-to-peer entity based on the generic
	BerryTella P2P framework.
	"""
	#--------------------------------------------------------------------------
	def __init__(self, maxpeers, serverport, model = False, directory = None):
	#--------------------------------------------------------------------------
		""" Initializes the peer to support connections up to maxpeers number
		of peers, with its server listening on the specified port. Also sets
		the dictionary of local files to empty and adds handlers to the
		BTPeer framework.
		"""

		BTPeer.__init__(self, maxpeers, serverport)
		self.addrouter(self.__router)
		# The below variable is set to true if and only if this node is a modeling node.
		self.model = model
		self.directory = directory
		self.received = dict()

		handlers = {
		LISTPEERS : self.__handle_listpeers,
		INSERTPEER : self.__handle_insertpeer,
		PEERNAME: self.__handle_peername,
		QUERY: self.__handle_query,
		PEERQUIT: self.__handle_quit,
		MODEL: self.__handle_model,
		FILEGET: self.__handle_fileget,
		# DATAREQ: self.__handle_datareq,
		QUERYREQ: self.__handle_queryreq,
		DATAQUERY: self.__handle_dataquery,
		VISREQ: self.__handle_visrequest,
		BUILDMODEL: self.__handle_buildmodel,
		 }

		for mt in handlers:
			self.addhandler(mt, handlers[mt])

		# end FilerPeer constructor

	#--------------------------------------------------------------------------
	def __debug(self, msg):
    	#--------------------------------------------------------------------------
		if self.debug:
			btdebug(msg)

	#--------------------------------------------------------------------------
	def __router(self, peerid):
	#--------------------------------------------------------------------------
		if peerid not in self.getpeerids():
			return (None, None, None)
		else:
			rt = [peerid]
			rt.extend(self.peers[peerid])
			return rt

	#--------------------------------------------------------------------------
	def __handle_insertpeer(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the INSERTPEER (join) message type. The message data
		should be a string of the form, "peerid	host	port", where peer-id
		is the canonical name of the peer that desires to be added to this
		peer's list of peers, host and port are the necessary data to connect
		to the peer.
		"""
		self.peerlock.acquire()
		try:
			try:
				peerid,host,port = data.split()

				if self.maxpeersreached():
					self.__debug('maxpeers %d reached: connection terminating'
						% self.maxpeers)
					peerconn.senddata(ERROR, 'Join: too many peers')
					return

				if peerid not in self.getpeerids() and peerid != self.myid:
					self.addpeer(peerid, host, port)
					self.__debug('added peer: %s' % peerid)
					peerconn.senddata(REPLY, 'Join: peer added: %s' % peerid)
				else:
					peerconn.senddata(ERROR, 'Join: peer already inserted %s'
							% peerid)
			except:
				self.__debug('invalid insert %s: %s' % (str(peerconn), data))
				peerconn.senddata(ERROR, 'Join: incorrect arguments')
		finally:
			self.peerlock.release()

		# end handle_insertpeer method

	#--------------------------------------------------------------------------
	def __handle_listpeers(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the LISTPEERS message type. Message data is not used. """
		self.peerlock.acquire()
		try:
			self.__debug('Listing peers %d' % self.numberofpeers())
			peerconn.senddata(REPLY, '%d' % self.numberofpeers())
			for pid in self.getpeerids():
				host,port = self.getpeer(pid)
				peerconn.senddata(REPLY, '%s %s %d' % (pid, host, port))
		finally:
				self.peerlock.release()

	#--------------------------------------------------------------------------
	def __handle_peername(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the NAME message type by sending the value of the myid variable
		through the BTPeerConnection peerconn. Message data is not used. """
		peerconn.senddata(REPLY, self.myid)

	#--------------------------------------------------------------------------
	def __handle_query(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the QUERY message type. The message data should be in the
		format of a string, "return-peer-id	key	ttl", where return-peer-id
		is the name of the peer that initiated the query, key is the (portion
		of the) file name being searched for, and ttl is how many further
		levels of peers this query should be propagated on.
		"""
		# self.peerlock.acquire()
		try:
			peerid, key, ttl = data.split()
			peerconn.senddata(REPLY, 'Query ACK: %s' % key)
		except:
			self.__debug('invalid query %s: %s' % (str(peerconn), data))
			peerconn.senddata(ERROR, 'Query: incorrect arguments')
			# self.peerlock.release()

		t = threading.Thread(target=self.__processquery,
						args=[peerid, key, int(ttl)])
		t.start()

	#--------------------------------------------------------------------------
	def __handle_quit(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the QUIT message type. The message data should be in the
		format of a string, "peer-id", where peer-id is the canonical
		name of the peer that wishes to be unregistered from this
		peer's directory.
		"""
		self.peerlock.acquire()
		try:
			peerid = data.lstrip().rstrip()
			if peerid in self.getpeerids():
				msg = 'Quit: peer removed: %s' % peerid
				self.__debug(msg)
				peerconn.senddata(REPLY, msg)
				self.removepeer(peerid)
			else:
				msg = 'Quit: peer not found: %s' % peerid
				self.__debug(msg)
				peerconn.senddata(ERROR, msg)
		finally:
			self.peerlock.release()
		# precondition: may be a good idea to hold the lock before going
		#				 into this function

	#--------------------------------------------------------------------------
	def model_datareq(self):
	#--------------------------------------------------------------------------
		""" Used to initiate data request to secondary modelling nodes.
		"""

		try:
			# Get list of all model peers reachable from the current node.
			model_peers = self.modelpeerlist(sys.maxsize) # TODO: confirm data type of model_peers
			results = []

			# Fetch data from secondary model nodes
			for peer in model_peers:
				print("Requesting game data from supernode at {}:{}...".format(peer[0],peer[1]))
				result = self.persistent_connectandsend(peer[0], peer[1], FILEGET, '')
				result = ''.join(result).strip()
				result = bytes.fromhex(result)
				result = pd.read_pickle(BytesIO(result), compression="xz")
				# result = peer.senddata(FILEGET)
				results.append(result)
				print("Data from supernode at {}:{} arrived successfully".format(peer[0],peer[1]))


			# Fetch local data on primary model node
			results.append(self.extract_model_files())
			print("Data from primary supernode {} received successfully".format(self.myid))
			# return combined data to calling function (build_model).
			return results

		except:
			traceback.print_exc()
		# finally:
		# 	# Remove temp file - prevent huge amount of data from being keep on a node
		# 	# after the request has been completed.
		# 	os.remove(path)

	#--------------------------------------------------------------------------
	def __handle_queryreq(self, peerconn, argument):
	#--------------------------------------------------------------------------
		""" Handles the QUERYREQ message type. This function is called by the node
		that receives a query request.

		Parameters:
		argument (str):
			Specifies the parameters to use in querying the collected data and is
			expected to be a parameter (mean, median, mode, variance, stdev),
			start date, and end data separated by commas.
		peerconn (BTPeerConnection):
			Connection to the peer requesting the query result.
		"""
		print("Received following query:", argument)
		try:
			# Get list of all model peers reachable from the current node.
			model_peers = self.modelpeerlist(sys.maxsize)
			print("List of peers found in network", model_peers)
			fd, path = tempfile.mkstemp()

			counts = []
			values = []
			node_num = 1
			parameter = argument.split(',')[0]
			error_line = 'Model peer {}: no data found'
			result_text = 'Individual model node results -\n'

			# Get query result for each model peer node and consolidate.
			for peer in model_peers:
				result = self.query(argument, peer)
				if result == 'None':
					text = error_line.format(node_num)
				else:
					text = self.queryreq_helper(counts, values, result, parameter, node_num)

				result_text += text + '\n'
				node_num += 1

			# Include query result for own data.
			self_query = self.dataquery(argument)
			if self_query == 'None':
				text = error_line.format(node_num)
			else:
				text = self.queryreq_helper(counts, values, self_query, parameter, node_num)
			result_text += text

			if parameter == 'mean' or parameter == 'variance' or parameter == 'stdev':
				# Calculate weighted averages of results.
				result = self.compute_summary_stat(parameter, counts, values)
				result_text = result + '\n' + result_text

			print("Sending query result:\n", result_text)
			with open(path, 'w') as tmp:
				tmp.write(result_text)

			# Send combined query results back to the requester.
			self.send_requested_data(peerconn, path)

		except:
			traceback.print_exc()
		finally:
			# Remove temp file - prevent huge amount of data from being keep on a node
			# after the request has been completed.
			os.remove(path)

	#--------------------------------------------------------------------------
	def compute_summary_stat(self, parameter, counts, values):
	#--------------------------------------------------------------------------
		""" Computes a summary statistic given the name of a statistic,
		an array of calculated values for that statistic, and an array containing
		the number of data samples used in calculating each of the individual
		values for that statistic.

		Parameters:
		parameter (str):
			Specifies the type of parameter (ex. 'stdev', 'variance', 'mean')
			contained in counts.
		counts (array of int):
			Array of calculated values of the specified parameter type.
		values (array of float):
			Values is an array such that the value at the i-th index is equal to the
			number of data samples used to calculate the i-th value in counts.

		Returns:
		A str specifying the calculated summary statistic.
		"""
		value_arr = np.array(values)
		count_arr = np.array(counts)
		if parameter == 'stdev':
			value_arr = np.square(value_arr)

		w_sum = np.dot(value_arr, count_arr)
		count_sum = np.sum(count_arr)

		if count_sum == 0:
			w_avg = 0
		else:
			w_avg = w_sum/count_sum

		if parameter == 'stdev':
			w_avg = math.sqrt(w_avg)
		if parameter == 'stdev' or parameter == 'variance':
			return f'Weighted average of {parameter} results - {w_avg:.3f}\n'
		else:
			return f'Mean of results - {w_avg:.3f}\n'

	#--------------------------------------------------------------------------
	def queryreq_helper(self, counts, values, result, parameter, node_num):
	#--------------------------------------------------------------------------
		"""Process a query result received from a different model node.

		Parameters:
		counts (array of int):
			Array of calculated values of the specified parameter type sent from
			previous model node peers in the network.
		values (array of float):
			Values is an array such that the value at the i-th index is equal to the
			number of data samples used to calculate the i-th value in counts.
		result (str):
			A tuple-convertible string specifying the number of rows used in
			calculating a parameter value and the calculated value itself that
			is to to be added to values.
		parameter (str):
			Specifies the type of parameter (ex. 'stdev', 'variance', 'mean')
			contained in counts.
		node_num(int):
			An id number for the peer that sent the calculations contained in
			result.

		Returns:
		A str specifying the information contained in the input argument result.
		"""
		result = make_tuple(result)
		if parameter == 'mean' or parameter == 'variance' or parameter == 'stdev':
			counts.append(int(result[0]))
			values.append(float(result[1]))
		value = float(result[2])
		return f'Model peer {node_num}: {value:.3f}'

	#--------------------------------------------------------------------------
	def query(self, argument, peer):
	#--------------------------------------------------------------------------
		'''
		Sends a message with message type DATAQUERY containing the query argument
		through a BTPeerConnection to the peer specified by the input argument peer.

		Parameters:
		argument (str):
			Specifies the parameters to use in querying the collected data and is
			expected to contain a parameter (mean, median, mode, variance, stdev),
			start date, and end data separated by commas.
		peer (tuple of str and int):
			A tuple with the first element specifying the IP address of the node
			to send the message to and the second element specifying the port of
			the node.

		Returns:
		A str specifying the query response from the model node specified by peer.
		'''
		print("Sending query request to peer", peer, ":", argument)
		resp = self.connectandsend( peer[0], peer[1], DATAQUERY, argument)
		resp = resp[0][1]
		print("Received result from peer", peer, ":", resp)
		resp = ''.join(resp).strip()
		return resp

	#--------------------------------------------------------------------------
	def dataquery(self, data):
	#--------------------------------------------------------------------------
		""" Runs a query on the data stored on the specific node.

		Parameters:
		data (str):
			Specifies the parameters to use in querying the collected data and is
			expected to contain a parameter (mean, median, mode, variance, stdev),
			start date, and end data separated by commas.

		Returns:
		A str specifying the result of executing the query on locally-collected
		data.
		"""
		filter = Filter()
		if 'game_data' not in os.listdir(self.directory):
			return str(None)

		parameters = data.split(',')
		path = os.path.join(self.directory, 'game_data')
		filter.filter(gdir=path, start_date=parameters[1], end_date=parameters[2])
		game_data = os.path.join(self.directory, 'filtered_game_data')
		health_data = os.path.join(self.directory, 'filtered_health_data')

		# No data for specified date range.
		if len(os.listdir(game_data)) == 0:
			return str(None)

		qq = QuickQuery()
		query_result = qq.descriptive_stats(parameters[0], 'heart_rate', game_data, health_data)
		return str(query_result)


	#--------------------------------------------------------------------------
	def __handle_dataquery(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the DATAQUERY message type. This function is called by a node
		that is to run a query on the data it has stored. The result of the query
		is sent back to the requester.

		Parameters:
		data (str):
			Specifies the parameters to use in querying the collected data and is
			expected to contain a parameter (mean, median, mode, variance, stdev),
			start date, and end data separated by commas.
		peerconn (BTPeerConnection):
			Connection to the peer requesting the query result.
		"""
		print("Received query request:", data)
		response = self.dataquery(data)
		print("Sending query response:", response)
		peerconn.senddata(QUERYSEND, response)


	#--------------------------------------------------------------------------
	def submitquery(self, peer, argument):
	#--------------------------------------------------------------------------
		""" Requests that a query is run on data stored on all modeling nodes
		reachable by the node defined by the input argument peer.

		Parameters:
		peer (tuple of str and int):
			A tuple where the first element is a string equal to the IP address of
			the node to which the request is being made and the second element
			is an int equal to the port of the node to which the request is being made.
		argument (str):
			Specifies the parameters to use in querying the collected data and is
			expected to contain a parameter (mean, median, mode, variance, stdev),
			start date, and end data separated by commas.

		Returns:
		A str reporting the received query results.
		"""
		try:
			result = self.persistent_connectandsend(peer[0], peer[1], QUERYREQ, argument)
		except:
			if self.debug:
				traceback.print_exc()
		print("Query result received:\n", ''.join(result).strip())
		return result

	#--------------------------------------------------------------------------
	def submitvisrequest(self, peer, argument):
	#--------------------------------------------------------------------------
		""" Requests that a visualization specified by argument is created for the
		data stored on a modeling node specified by peer.

		Parameters:
		peer (tuple of str and int):
			A tuple where the first element is a string equal to the IP address of the
			node to which the request is being made and the second element is an int
			equal to the port of the node to which the request is being made.
		argument (str):
			Specifies the visual to create and contains the name of a game and a feature
			of recorded health data separated by a comma.

		Result:
		The bytes for the .png image of the created visual.
		"""
		try:
			result = self.persistent_connectandsend(peer[0], peer[1], VISREQ, argument)
		except:
			if self.debug:
				traceback.print_exc()

		result = ''.join(result).strip()
		print("Received a visualization result", len(bytes.fromhex(result)), "bytes")
		return result

	#--------------------------------------------------------------------------
	def __handle_visrequest(self, peerconn, argument):
	#--------------------------------------------------------------------------
		""" Requests that a visual is created using the data stored on the node
		and the parameters specified by the input argument.

		Parameters:
		peerconn (BTPeerConnection):
			Connection to the peer requesting the visualization.
		argument (str):
			Specifies the visual to create and contains the name of a game and a feature
			of recorded health data separated by a comma.
		"""
		args = argument.split(',')
		game = args[0]
		feature = args[1]
		print("Received visualization request:", argument)
		if 'game_data' in os.listdir(self.directory):
			path = os.path.join(self.directory, 'game_data')
			filter = Filter()
			filter.filter(gdir=path, game=game)
			print("hello_again")
			vis = Visualize()
			path = vis.visualize(os.path.join(self.directory, 'filtered_game_data'), feature)
		else:
			text = 'No data found to visualize: Model node\'s data \ndirectory may be incorrectly configured'
			path = 'error.png'
			texttoimage.convert(text, image_file=path, font_size=50, color='black')
		print("Sending back a visualization response with", len(open(path, 'rb').read()), "bytes")
		self.send_requested_data(peerconn, path)
		os.remove(path)

	#--------------------------------------------------------------------------
	def read_as_bytes(self, filepath):
	#--------------------------------------------------------------------------
		""" Determines whether the file with a path specified by filepath should
		be read as bytes when its data is sent across the network.

		Parameters:
		filepath (str):
			The filepath of the file to be sent across the network.

		Return:
		A bool indicating whether the file with a path of filepath should be
		read as bytes.
		"""
		filepath_elements = filepath.split('.')
		filetype = filepath_elements[-1]

		if len(filepath_elements) == 1 or (filetype != 'png' and filetype != 'xz'):
			return False
		return True

	#--------------------------------------------------------------------------
	def send_requested_data(self, peerconn, filepath):
	#--------------------------------------------------------------------------
		""" Sends the data contained in the file with a path equal to filepath through
		the BTPeerConnection opened with persistent_connectandsend to the node on the
		other end of the connection.

		Parameters:
		peerconn (BTPeerConnection):
			Connection to the peer to send the file data to.
		filepath (str):
			The filepath of the file whose data is to be sent across the network.
		"""
		read_size = 2048
		fd = None
		# Stores whether the file is to be read as bytes.
		byte_reading = False
		chunk_number = 10

		try:
			if self.read_as_bytes(filepath):
				fd = open(filepath, 'rb')
				byte_reading = True
				chunk_number = 5
			else:
				fd = open(filepath, 'r')

			filedata = ''
			i = 0
			while True:
				data = fd.read(read_size)
				if not len(data):
					# EOF reached.
					while (len(filedata) % 2048) != 0:
						filedata += " "
					# Note: FILESEND does not have a function handler. The msgtype
					# does not seem to matter here, but has previously been used
					# in debugging to make sure that the receiver was receiving
					# the proper message type.
					peerconn.senddata(FILESEND, filedata)
					break

				if byte_reading:
					filedata += data.hex()
				else:
					filedata += data
				i += 1

				if (i % chunk_number) == 0:
					while(len(filedata) % 2048) != 0:
						filedata += " "
					peerconn.senddata(FILESEND, filedata)
					filedata = ''

		except:
			traceback.print_exc()
			self.__debug('Error reading file %s' % fname)

		finally:
			# Send a message so the connection can be closed in persistent_connectandsend.
			peerconn.senddata(REPLY, "DONE")
			if fd != None:
				fd.close()

	#--------------------------------------------------------------------------
	def makerequest(self, peer, intercept):
	#--------------------------------------------------------------------------
		""" Requests data from all modeling nodes reachable by the node defined by
		the input argument peer. The peer is expected to be a tuple where the first
		element is a string equal to the IP address of the node to which the request
		is being made and the second element is an int equal to the port of the node
		to which the request is being made. The game_name should be a string with
		specific information about the request.
		"""
		try:
			result = self.persistent_connectandsend(peer[0], peer[1], BUILDMODEL, intercept)
		except:
			if self.debug:
				traceback.print_exc()

		return result


	#--------------------------------------------------------------------------
	def modelpeerlist(self, hops=1):
	#--------------------------------------------------------------------------
		"""
		Constructs a list of model peers reachable from the current node within a
		number of hops equal to the input argument hops, which should be an integer.

		Parameters:
		hops (int):
			Specifies the depth of the depth-first search to be performed through
			the network for model peers

		Returns:
		An array of tuples specifying model peers found in the network, where the
		elements at index 0 are peer IP addresses, and the elements at index 1
		are peer port numbers.
		"""
		seen = set()
		peers = []

		try:
			print("Generating a list of supernodes in the network")
			for pid in self.getpeerids():
				host,port = self.getpeer(pid)
				self.modelpeerlisthelper(host, port, seen, peers, hops)
		except:
			if self.debug:
				traceback.print_exc()

		return peers

	#--------------------------------------------------------------------------
	def modelpeerlisthelper(self, host, port, seen, peers, hops=1):
	#--------------------------------------------------------------------------
		"""
		Helper for the modelpeerlist method. If hops is greater than 0 and the node
		specified by the input arguments host and port is not included in the input
		argument seen, adds the node to seen, adds the node to the input array peers
		if it is a model node and then calls the method recursively on each of the
		node's peers with hops decremented by 1.

		Parameters:
		host (str):
			The IP address of a node in the network
		port (int):
			An int equal to the port of the node with IP address specified by host
		seen (set of str):
			A set containing the peerid's of all nodes seen so far in the search for
			model nodes
		peers (array of tuples of str and int):
			An array containing tuples specifying the model nodes found so far in the
			search for model nodes. For each tuple, the elements at index 0 are peer
			IP addresses, and the elements at index 1 are peer port numbers
		hops (int):
			Specifies the depth of the depth-first search to be performed through
			the network for model peers
		"""
		if not hops:
			return

		self.__debug("Searching for model peer from (%s,%s)" % (host,port))

		try:
			_, peerid = self.connectandsend(host, port, PEERNAME, '')[0]
			self.__debug("contacted " + peerid)

			if peerid in seen:
				# Peer has already been explored.
				return
			else:
				seen.add(peerid)

			# Check if the peer represented by host and port is a model node.
			print("Asking if peer at", "{}:{}".format(host, str(port)), "is a supernode")
			resp = self.connectandsend(host, port, MODEL, '')[0]
			self.__debug(str(resp))
			print("Supernode response for peer at", "{}:{}".format(host, str(port)), "is:", resp[1])
			if (resp[0] == REPLY) and (resp[1] == 'True'):
				# Peer is a model node.
				peers.append((host, int(port)))

			# Do recursive depth first search to find more peers.
			resp = self.connectandsend(host, port, LISTPEERS, '',
					pid=peerid)

			if len(resp) > 1:
				resp.reverse()
				resp.pop()	# get rid of header count reply
				while len(resp):
					nextpid,host,port = resp.pop()[1].split()
					if nextpid != self.myid:
						self.modelpeerlisthelper(host, port, seen, peers, hops - 1)

		except:
			if self.debug:
				traceback.print_exc()

	#--------------------------------------------------------------------------
	def modelpeersearch(self, hops=1):
	#--------------------------------------------------------------------------
		"""
		Searches the network for a single model node reachable from the current node
		within a number of hops equal to the input argument hops, which should be an
		integer.

		Parameters:
		hops (int):
			Specifies the depth of the depth-first search to be performed through
			the network for model peers

		Returns:
		A tuple where the first element is a string equal to the IP address of a model
		node and the second element is an int equal to the port of the model node.
		"""
		seen = set()

		try:
			print("Searching for a supernode in the network to become a primary supernode")
			for pid in self.getpeerids():
				host,port = self.getpeer(pid)
				result = self.modelpeersearchhelper(host, port, seen, hops)
				print("Primary supernode is:", result)
				if result is not None:
					return result

		except:
			if self.debug:
				traceback.print_exc()

	#--------------------------------------------------------------------------
	def modelpeersearchhelper(self, host, port, seen, hops=1):
	#--------------------------------------------------------------------------
		"""
		Helper for the modelpeersearch method. If hops is greater than 0 and the node
		specified by the input arguments host and seen is not represented in the input
		set seen, checks if the node specified by host and port is a model node, and
		if so, returns a tuple where the first element is host and the second is port
		cast to an int. Otherwise, calls the method recursively on each of the peers
		of the node represented by host and port with host decremented by 1.
		argument seen, adds the node to seen, adds the node to the input array peers
		if it is a model node and then calls the method recursively on each of the
		node's peers with hops decremented by 1.

		Parameters:
		host (str):
			The IP address of a node in the network
		port (int):
			An int equal to the port of the node with IP address specified by host
		seen (set of str):
			A set containing the peerid's of all nodes seen so far in the search for
			model nodes
		hops (int):
			Specifies the depth of the depth-first search to be performed through
			the network for model peers
		"""

		if not hops:
			return

		self.__debug("Searching for model peer from (%s,%s)" % (host,port))

		try:
			_, peerid = self.connectandsend(host, port, PEERNAME, '')[0]
			self.__debug("contacted " + peerid)

			if peerid in seen:
				# Peer has already been explored.
				return None
			else:
				seen.add(peerid)

			# Check if the peer represented by host and port is a model node.
			print("Asking if peer at", "{}:{}".format(host, str(port)), "is a supernode")
			resp = self.connectandsend(host, port, MODEL, '')[0]
			self.__debug(str(resp))
			print("Supernode response for peer at", "{}:{}".format(host, str(port)), "is:", resp[1])
			if (resp[0] == REPLY) and (resp[1] == 'True'):
				# Peer represented by host and port is a model node.
				return (host, int(port))

			# Do recursive depth first search to find more peers.
			resp = self.connectandsend(host, port, LISTPEERS, '',
					pid=peerid)

			if len(resp) > 1:
				resp.reverse()
				resp.pop()	# get rid of header count reply
				while len(resp):
					nextpid,host,port = resp.pop()[1].split()
					if nextpid != self.myid:
						result = self.modelpeersearchhelper(host, port, seen, hops - 1)
						if result is not None:
							return result
		except:
			print("ERROR ", traceback.print_exc())
			if self.debug:
				traceback.print_exc()

	#--------------------------------------------------------------------------
	def __handle_model(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the MODEL message type by sending the value of the model
		variable through the BTPeerConnection peerconn. Message data is not used.

		Parameters:
		peerconn (BTPeerConnection):
			Connection to the peer requesting the value of the model instance
			variable.
		"""
		print("Replying that this node's supernode status is:", self.model)
		peerconn.senddata(REPLY, str(self.model))

	#--------------------------------------------------------------------------
	def persistent_connectandsend( self, host, port, msgtype, msgdata,
		pid=None, waitreply=True ):
	#--------------------------------------------------------------------------
		"""
		persistent_connectandsend( host, port, message type, message data, peer id,
		wait for a reply ) -> [ first reply data , second reply data ... ]

		Connects and sends a message to the specified host:port. The reply/replies
		from the node specified by host:port are added to the array msgreply until
		a reply with a message type of REPLY is received.

		Parameters:
		host (str):
			The IP address of a node to connect to
		port (int):
			An int equal to the port of the node to connect to
		msgtype (str):
			The type of the message to send to the peer specified by host:port
		msgdata (str):
			The the content of the message to send to the peer specified by host:port

		Returns:
		An array of str specifying the response data received from the contacted peer.
		"""

		msgreply = []
		try:
			peerconn = BTPeerConnection( pid, host, port, debug=self.debug )
			peerconn.senddata( msgtype, msgdata )
			self.__debug( 'Sent %s: %s' % (pid, msgtype) )

			while True:
				onereply = peerconn.recvdata()
				if (onereply[0] == REPLY):
					break
				msgreply.append( onereply[1] )

			peerconn.close()
		except KeyboardInterrupt:
			raise
		except:
			traceback.print_exc()
			if self.debug:
				traceback.print_exc()

		return msgreply

	#--------------------------------------------------------------------------
	def __handle_fileget(self, peerconn, data):
	#--------------------------------------------------------------------------
		""" Handles the FILEGET message type by sending the value of the model
		variable through the BTPeerConnection peerconn.

		Method is used to extract, compress and send all game data to a requesting
		primary model node
		"""
		print("FILEGET request received ")
		self.peerlock.acquire()

		game_dir = self.directory + "/game_data"
		compressed_file_path = game_dir + '/all_game_df.xz'

		try:
			all_game_df = self.extract_model_files()

			# if no data is found
			if 'NO DATA' in all_game_df:
    				print("No game data found on {}. Sending a 'NO DATA' message to {}:{}...".format(self.myid, peerconn.host, peerconn.port ))
    				peerconn.senddata(REPLY, all_game_df)


			# if data exists
			else:
				print("Preparing to send compressed game data on {} to supernode at {}:{}...".format(self.myid, peerconn.host, peerconn.port))
				# Save and compress game data
				all_game_df.to_pickle(compressed_file_path)

				# Send compressed data from each reachable model node back to the requester.
				self.send_requested_data(peerconn, compressed_file_path)
				print("Game data on {} sent to supernode at {}:{}...".format(self.myid, peerconn.host, peerconn.port))



		except:
			traceback.print_exc()
		finally:
			# Remove temp file - prevent huge amount of data from being keep on a node
			# after the request has been completed.
			os.remove(compressed_file_path)
			print("Deleted compressed game data on {}".format(self.myid))
			self.peerlock.release()



	#--------------------------------------------------------------------------
	def extract_model_files(self):
	#--------------------------------------------------------------------------
		""" Used to extract all game data used for model building into a single dataframe.
		"""

		print("Checking for game data on supernode at {}".format(self.myid))

		game_dir = self.directory + "/game_data"
		# Fetch all file names in the game directory
		game_files = [ i for i in os.listdir(game_dir) if 'csv' in i]

		# Check that there is game data available
		if len(game_files) > 0:
			print("Found game data on supernode at {}".format(self.myid))
			dataframes = []
			for i in game_files:
				i = os.path.join(game_dir, i)
				game_df = pd.read_csv(i, parse_dates=["timestamp"])
				#game_df["game"] = i.split(".")[0].rsplit("_")[-1] # adds name of the game that has the data
				game_df["game"] = i.split(".")[-2].rsplit("_")[-1]
				dataframes.append(game_df)

			# Merge all game data
			print("Extracted game data on supernode at {}.".format(self.myid))
			return pd.concat(dataframes)

		else:
    			return 'NO DATA FROM {}'.format(self.myid)



	#--------------------------------------------------------------------------
	def __handle_buildmodel(self, peerconn, intercept):
	#--------------------------------------------------------------------------
		""" Used to build model from game data across all nodes in the network
		"""

		print("Received build model message...")

		self.peerlock.acquire()

		try:
			print("Fetching data from other super nodes...")
			all_df_compressed = self.model_datareq()
			print("Data from all supernodes returned")

			# Filter out empty data
			# all_df_compressed = [i for i in all_df_compressed if 'NO DATA' not in i]
			all_dfs = []
			for ind, compressed_df in enumerate(all_df_compressed):
				if ind != len(all_df_compressed) - 1:
					if 'NO DATA' not in compressed_df:
						print("Casting recieved data to the correct types...")
						compressed_df['timestamp'] = pd.to_datetime(compressed_df['timestamp'])
						compressed_df['heart_rate'] = compressed_df['heart_rate'].astype(int)
						compressed_df['steps'] = compressed_df['steps'].astype(int)
						compressed_df['distance(miles)'] = compressed_df['distance(miles)'].astype(float)
						compressed_df['active_calories_burned'] = compressed_df['active_calories_burned'].astype(float)

						compressed_copy = compressed_df[['timestamp', 'heart_rate', 'steps', 'distance(miles)', 'active_calories_burned']]
						df = compressed_copy.diff()[:-1] # generates changes in values with each time period of 1 min
						df['game'] = compressed_df['game'].to_list()[1:]
						df = df[1:]
						all_dfs.append(df)

				else:
					if 'NO DATA' not in compressed_df:
						# Last entry is local data and wasn't compressed so merge immediately
						compressed_copy = compressed_df[['timestamp', 'heart_rate', 'steps', 'distance(miles)', 'active_calories_burned']]
						df = compressed_copy.diff()[:-1] # generates changes in values with each time period of 1 min
						df['game'] = compressed_df['game'].to_list()[1:]
						df = df[1:]
						all_dfs.append(df)

			# Merging all dataframes
			print("Merging all data from all supernodes...")
			data_df = pd.concat(all_dfs)
			data_df['index'] = range(data_df.shape[0])

			# create one-hot encoding of game column
			print("Encoding game names using one-hot encoding...")
			one_hot_game = pd.get_dummies(data_df[['game']])
			one_hot_game['index'] = range(data_df.shape[0])

			X, y = data_df.drop(labels=['timestamp','heart_rate','game'], axis=1), data_df['heart_rate'].values

			# Merge data
			all_X = pd.merge(X,one_hot_game)
			all_X = all_X.drop(labels=['index'], axis=1)


			# Split data
			print("Splitting the data into training and testing...")
			train_stop_idx = round(X.shape[0] * 0.8)
			X_train, X_test = all_X[:train_stop_idx], all_X[train_stop_idx+1:]
			y_train, y_test = y[:train_stop_idx], y[train_stop_idx+1:]

			# Scale data
			print("Scaling the data...")
			scaler = MinMaxScaler()
			X_train_scaled = scaler.fit_transform(X_train)
			X_test_scaled = scaler.transform(X_test)

			# train model
			if intercept == "yes":
				param = True
			else:
				param = False
			print("Training the model...")
			estimator = LinearRegression(fit_intercept = param)
			estimator.fit(X_train_scaled, y_train)

			# test model
			print("Evaluating the model...")
			y_predicted = estimator.predict(X_test_scaled)

			mae = metrics.mean_absolute_error(y_test, y_predicted)
			mse = metrics.mean_squared_error(y_test, y_predicted)
			r2 = metrics.r2_score(y_test, y_predicted)

			print("Model results:\n Mean Absoluted Error:{},\nMean Square Error:{},\nR_Squared:{}".format(mae,mse,r2))
			# send model and test result
			peerconn.senddata(FILESEND,"Mean Absoluted Error:{},\nMean Square Error:{},\nR_Squared:{}".format(mae,mse,r2))
			print("Sending the model results back to client node at {}:{}".format(peerconn.host, peerconn.port))
			peerconn.senddata(REPLY,"")
			# TODO: Implement code to send actual model.


		except:
			traceback.print_exc()
		finally:

			self.peerlock.release()




	#--------------------------------------------------------------------------
	def buildpeers(self, host, port, hops=1):
	#--------------------------------------------------------------------------
		""" buildpeers(host, port, hops)
		Attempt to build the local peer list up to the limit stored by
		self.maxpeers, using a simple depth-first search given an
		initial host and port as starting point. The depth of the
		search is limited by the hops parameter.
		"""
		if self.maxpeersreached() or not hops:
			return

		peerid = None

		self.__debug("Building peers from (%s,%s)" % (host,port))

		try:
			_, peerid = self.connectandsend(host, port, PEERNAME, '')[0]
			self.__debug("contacted " + peerid)
			resp = self.connectandsend(host, port, INSERTPEER,
					'%s %s %d' % (self.myid,
							self.serverhost,
							self.serverport))[0]
			self.__debug(str(resp))
			if (resp[0] != REPLY) or (peerid in self.getpeerids()):
				return

			self.addpeer(peerid, host, port)

			# do recursive depth first search to add more peers
			resp = self.connectandsend(host, port, LISTPEERS, '',
					pid=peerid)

			if len(resp) > 1:
				resp.reverse()
				resp.pop()	# get rid of header count reply
				while len(resp):
					nextpid,host,port = resp.pop()[1].split()
					if nextpid != self.myid:
						self.buildpeers(host, port, hops - 1)
		except:
			if self.debug:
				traceback.print_exc()
			self.removepeer(peerid)
