
from exchange import Okcoin
from bitfinex import Bitfinex
from exchange import GLOBAL_DICT
from threading import Thread
import time

def main():
    okcoin = Okcoin(deploy=True)
    okcoin.add_tickers(['btc'])
    okcoin.run_forever()

    bitfinex = Bitfinex(deploy=True)
    bitfinex.add_ticker(['btc'])
    bitfinex.run_forever()

    t = Thread(target=print_global_dict,args=())
    t.daemon = True
    t.start()

    try:
        while True: time.sleep(2)
    except KeyboardInterrupt as e:
        print e

def print_global_dict():
    while True:
        print GLOBAL_DICT
        time.sleep(2)

if __name__ == '__main__':
    main()
