
import websocket
from threading import Thread
import time
import json
from exchange import GLOBAL_DICT
#import couchdb
#from storage import RelaxedCouch

class Logic:

	threshold = 10


	def __init__(self, deploy=False):
		self.deploy = deploy


	def run_forever(self, delay=None):

		if delay is not None: time.sleep(delay)
		self.t = Thread(target=self.run,args=())
		self.t.daemon = True
		self.t.start()


	def run(self):

		#iterates through all tickers, trades if price differential is > threshold


		while True:

			for ticker in GLOBAL_DICT.keys():

				self.get_prices(ticker)


				if self.max_price - self.min_price > self.threshold:
					self.trade(ticker, self.min_exchange, self.max_exchange)

			time.sleep(1)



	# updates min and max prices for a ticker
	def get_prices(self, ticker):

		self.max_price = 0
		self.min_price = 99999
		self.min_exchange = "No min exchange"
		self.max_exchange = "No max exchange"

		for exchange in GLOBAL_DICT[ticker].keys():

			ask = GLOBAL_DICT[ticker][exchange]["ask"]
			bid = GLOBAL_DICT[ticker][exchange]["bid"]

			if bid > self.max_price:
				self.max_price = bid
				self.max_exchange = exchange
			if ask < self.min_price:
				self.min_price = ask
				self.min_exchange = exchange


	#places a trade for a given ticker at the buy and short exchanges
	def trade(self,ticker, buy,short):
		print "Buying "+buy+", shorting "+short
		print "max price = "+str(self.max_price)
		print "min price = "+str(self.min_price)
