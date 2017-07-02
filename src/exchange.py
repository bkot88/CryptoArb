
import websocket
from threading import Thread
import time
import json
import couchdb
from storage import RelaxedCouch

GLOBAL_DICT = {'BTC':{},'LTC':{},'ETH':{}}

class Okcoin:

    def __init__(self, deploy=False):

        # For RelaxedCouch, put in database name, username, password 
        self.db = RelaxedCouch('okcoin','admin','admin')
        self.deploy = deploy
        self.requests = []

        # Websocket URI of the exchange
        self.url = 'wss://real.okcoin.com:10440/websocket/okcoinapi'        
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open

    def run_forever(self, delay=None):
        # non-blocking call to run_forever
        if delay is not None: time.sleep(delay)
        self.t = Thread(target=self.ws.run_forever,args=())
        self.t.daemon = True # so that it can be keyboard interrupted
        self.t.start()

    def on_message(self, ws, msg):
        if 'result' in msg:
            print msg
            print ''
        else:
            doc = self.make_doc(msg)
            # add to global memory
            GLOBAL_DICT[doc['ticker']]['okcoin'] = {'ask':doc['ask'],'bid':doc['bid']}
            # self.db.async_save(doc)

    def on_error(self, ws, error):
        print error

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

    def make_doc(self, msg):
        '''
        
        '''
        # response view @ https://www.okcoin.com/ws_api.html
        json_msg = json.loads(msg)[0]
        doc = {}
        
        # build the ticker
        if 'ltc' in json_msg['channel']: ticker = 'LTC'
        elif 'btc' in json_msg['channel']: ticker = 'BTC'
        elif 'eth' in json_msg['channel']: ticker = 'ETH'
        else: ticker = ''
        doc['ticker'] = ticker

        # this identifies if the response is a ticker
        if 'timestamp' in json_msg['data']:
            # create a key made of timestamp and channel
            doc['timestamp'] = str(json_msg['data']['timestamp'])
            doc['_id'] = '({},{})'.format(json_msg['data']['timestamp'],ticker)
            doc['channel'] = json_msg['channel']
            doc['ask'] = json_msg['data']['sell']
            doc['bid'] = json_msg['data']['buy']
            doc['exchange'] = 'okcoin'
            return doc
        else: return json_msg

    def add_tickers(self,tickers):
        for ticker in tickers:
            request = '{{\'event\':\'addChannel\',\'channel\':\'ok_sub_spotusd_{}_ticker\'}}'.format(ticker)
            self.requests.append(request)
