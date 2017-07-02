
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
		self.t.start()


	def run(self):

		#iterates through all tickers, trades if price differential is > threshold


		while True:

			for ticker in GLOBAL_DICT.keys():

				get_prices(ticker)

				if max_price - min_price > threshold:
					trade(ticker, min_exchange, max_exchange)



	# updates min and max prices for a ticker
	def get_prices(ticker):

		max_price = 0
		min_price = 99999
		min_exchange = "No min exchange"
		max_exchange = "No max exchange"

		for exchange in GLOBAL_DICT[ticker].keys():

			ask = GLOBAL_DICT[ticker][exchange]["ask"]
			bid = GLOBAL_DICT[ticker][exchange]["bid"]

			if bid > max_price:
				max_price = bid
				max_exchange = exchange
			if ask < min_price:
				min_price = ask
				min_exchange = exchange


	#places a trade for a given ticker at the buy and short exchanges
	def trade(ticker, buy,short):
		print "Buying "+buy+", shorting "+short
