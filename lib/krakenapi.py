"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

import requests
import json
import yaml

class krakenfAPI():

    def __init__(self):
        self.baseURL = "https://api.kraken.com/0/"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)


    def getTicker(self):
        payload = {'pair': 'XXBTZJPY'}
        response = requests.get(self.baseURL + "public/Ticker", params=payload)

        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ticker = json.loads(response.text)
        bid = float(ticker["result"]["XXBTZJPY"]["b"][0])
        ask = float(ticker["result"]["XXBTZJPY"]["a"][0])

        print "kraken_ask :" + str(ask)
        print "kraken_bid :" + str(bid)

        return ask, bid

    def ask(self, rate, amount):

        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'API-Sign': self.config["kraken"]["API_SECRET"]
        }
        data = {
            'pair': 'XXBTZJPY',
            'type': 'buy',
            'ordertype': 'market',
            'volume:': amount
        }
        '''
        data = {
            'pair': 'XXBTZJPY',
            'type': 'buy',
            'ordertype': 'limit',
            'price': rate,
            'volume:': amount
        }
        '''

        response = requests.get(self.baseURL + "private/AddOrder", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response


    def bid(self, rate, amount):
        
        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'API-Sign': self.config["kraken"]["API_SECRET"]
        }
        data = {
            'pair': 'XXBTZJPY',
            'type': 'sell',
            'ordertype': 'market',
            'volume:': amount
        }
        '''
        data = {
            'pair': 'XXBTZJPY',
            'type': 'sell',
            'ordertype': 'limit',
            'price': rate,
            'volume:': amount
        }
        '''

        response = requests.get(self.baseURL + "private/AddOrder", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response


if __name__ == '__main__':
    #api = krakenfAPI()
    #api.getTicker()
    pass
