"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

from coincheck import market
from coincheck import order
from coincheck import account
import yaml

class CoincheckAPI():

    def __init__(self):
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def getTicker(self):
        m1 = market.Market()
        ticker =  m1.ticker()
    
        ask = ticker["ask"]
        bid = ticker["bid"]
    
        print "cc_ask :" + str(ask)
        print "cc_bid :" + str(bid)
        return ask,bid
        
    def ask(self, rate, amount):
        o1 = order.Order(access_key=self.config["coincheck"]["ACCESS_KEY"], secret_key=self.config["coincheck"]["API_SECRET"])
        print(o1.buy_btc_jpy(rate=rate, amount=amount))

    def bid(self, price, amount):
        o1 = order.Order(access_key=self.config["coincheck"]["ACCESS_KEY"], secret_key=self.config["coincheck"]["API_SECRET"])
        print(o1.sell_btc_jpy(rate=rate,amount=amount))

if __name__ == '__main__':
    #api = CoincheckAPI()
    #api.getTicker()
    pass
