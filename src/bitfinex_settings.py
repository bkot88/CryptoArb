url_wss = "wss://api.bitfinex.com/ws"

# SETTINGS 
db_host = '10.0.0.119'
db_name    = 'bitfinex'
db_user    = 'admin'
db_pw  	   = 'admin'


# Bitfinex supported pairs 
pairs  = "BTCUSD, LTCUSD, ETHUSD, ETCUSD, BFXUSD, RRTUSD, ZECUSD"

# List of elements for a ticker response 
ticker_keys = [ 
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

