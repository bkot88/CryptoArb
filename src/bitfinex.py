# -*- coding: utf-8 -*-
'''
A class represents connection with Bitfinex 
'''
import websocket
import time
import json
from threading import Thread
import bitfinex_settings as settings 
from storage import RelaxedCouch
from exchange import GLOBAL_DICT

# +-----------------------------------------------------------------+
''' WEBSOCKET handling '''

class Bitfinex:

	# Exchange Connection
	url_wss = settings.url_wss

	# Ticker
	ticker_keys = [ 
		'CHANNELID',
		'BID',	
		'BID_SIZE',
		'ASK',
		'ASK_SIZE',
		'DAILY_CHANGE',
		'DAILY_CHANGE_PERC',
		'LAST_PRICE',
		'VOLUME',
		'HIGH',
		'LOW'
	]

	# DATABASE 
	db_name = settings.db_name
	db_user = settings.db_user
	db_pw	= settings.db_pw
	db_host = settings.db_host


	def __init__(self, deploy=False):
		# deploy = True to run forever
		self.deploy = deploy 

		# For RelaxedCouch, put in database name, username, password 
		self.db = RelaxedCouch(self.db_name, self.db_user, self.db_pw, self.db_host)

		# self.db = RelaxedCouch('bitfinex', 'admin', 'admin', '10.0.0.119')

        # list of tickers to subscribe
		self.requests = []

		# Bitfinex connection info 
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp(self.url_wss, 
			on_message = self.on_message, 
			on_error = self.on_error, 
			on_close = self.on_close)
		self.ws.on_open = self.on_open

		# Subscription Status
		self.event   = ""
		self.channel = ""
		self.chanId  = ""
		self.pair 	 = ""

	def run_forever(self, delay=None):
        # non-blocking call to run_forever
		if delay is not None: time.sleep(delay)
		self.t = Thread(target=self.ws.run_forever,args=())
		self.t.start()

	def on_message(self, ws, message):
		self.process_msg(message)
	    
	def on_error(self, ws, error):
		print "Error: ", error

	def on_open(self, ws):
		# do an iteration here instead
		for request in self.requests:
			print request
			ws.send(request)
		if self.deploy is not True:
		# if deploy is not True exit the program after some seconds 
			seconds = 15
			Thread(target=self.dev_close,args=(seconds,)).start()

	def on_close(self, ws):
	    print 'closing', self.url
	    if self.deploy is True:
	        print 'reopening connection'
	        Thread(target=self.run_forever,args=(10,)).start()

	def dev_close(self, seconds):
	    print 'will close connection in ', seconds
	    print ''
	    time.sleep(seconds)
	    self.ws.close()

	def process_msg(self, msg):
		'''
    	When receiving a message from the api 
    	process the message, either print it 
    	or create a doc and save to couchdb
		'''
		print msg 
		msg = json.loads(msg)
		
		if isinstance(msg, dict):
			event = msg['event']
			print "Event is", event

			if "info" in event and "version" in msg:
				print "version", msg['version']

			elif "info" in event and "code" in msg:
				if '20051' in msg['code']:
					print "Stop/Restart Websocket Server (please try to reconnect) \n"
				if '20060' in msg['code']:
					print "Please pause any activity and resume after receiving the info message 20061 (it should take 10 seconds at most).\n"
				if '20061' in msg['code']:
					print "Done Refreshing data from the Trading Engine. You can resume normal activity. It is advised to unsubscribe/subscribe again all channels.\n"

			elif "subscribed" in event:
				print "Event is ", event 
				self.event 	 = event
				self.channel = msg['channel']
				self.chanId  = msg['chanId']
				self.pair    = msg['pair']
				print "Subscribed successfully to channel \"%s\" with channel ID %s for the pair %s" % (self.channel, self.chanId, self.pair)

			elif "pong" in event: print "pong"

			elif "error" in event: print msg

		elif isinstance(msg, list):
			if 'hb' in msg: print msg
			# if api sends pricing data, create doc and save to couchdb DB
			elif any(isinstance(i, list) for i in msg) is False:
				# print [(i,j) for i, j in zip(self.ticker_keys, msg)]
				doc = self.make_doc(msg)
				GLOBAL_DICT[doc['ticker']]['bitfinex'] = doc
				# print doc 
				self.db.async_save(doc)


	def make_doc(self, msg):
		'''
		Process api response to create a doc for couchdb
		'''
		# ['ticker','ask','bid','exchange','channel']
		doc = {}

		if self.pair != "":
			ticker = self.pair[0:3]
			doc['ticker']  = ticker 
			doc['channel'] = self.channel
			doc['ask']	   = msg[3]
			doc['bid']	   = msg[1]
			doc['exchange']= 'bitfinex'
		return doc 

	def add_ticker(self, tickers):
		for ticker in tickers:
			# message to send 
			ticker = ticker.upper() + 'USD'
			request = "{{\"event\":\"subscribe\",\"channel\":\"ticker\",\"pair\":\"{}\"}}".format(ticker)
			self.requests.append(request)



if __name__ == '__main__':
	bitfinex = Bitfinex()
