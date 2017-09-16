"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

import requests
import json
import yaml
import time

class CoincheckAPI():

    def __init__(self):
        self.baseURL = "https://coincheck.com/"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)


    def getTicker(self):
        #payload = {'pair': 'XXBTZJPY'}
        response = requests.get(self.baseURL + "api/ticker")

        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ticker = json.loads(response.text)
        bid = ticker["bid"]
        ask = ticker["ask"]

        print "coincheck_ask :" + str(ask)
        print "coincheck_bid :" + str(bid)

        return ask, bid

    def ask(self, rate, amount):
        headers = {
            'ACCESS-KEY': self.config["kraken"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': self.config["kraken"]["API_SECRET"],
            'ACCESS-NONCE':  int(time.time())
        }
        data = {
            "amarket_buy_amount": amount,
            "order_type": "market_buy",
            "pair": "btc_jpy"
        }

        '''
        data = {
            "amount": amount,
            "order_type": "buy",
            "pair": "btc_jpy"
        }
        '''

        response = requests.post(self.baseURL + "api/exchange/orders", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response


    def bid(self, rate, amount):
        headers = {
            'ACCESS-KEY': self.config["kraken"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': self.config["kraken"]["API_SECRET"],
            'ACCESS-NONCE':  int(time.time())
        }
        data = {
            "amount": amount,
            "order_type": "market_sell",
            "pair": "btc_jpy"
        }

        '''
        data = {
            "rate": rate,
            "amount": amount,
            "order_type": "sell",
            "pair": "btc_jpy"
        }
        '''

        response = requests.post(self.baseURL + "api/exchange/orders", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response



if __name__ == '__main__':
    #api = CoincheckAPI()
    #api.getTicker()
    pass
