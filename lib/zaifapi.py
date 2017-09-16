"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

import requests
import json
import yaml
import time


class ZaifAPI():

    def __init__(self):
        self.baseURL = "https://api.zaif.jp/api/1/"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def getTicker(self):
        response = requests.get(self.baseURL + "ticker/btc_jpy")
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ticker = json.loads(response.text)
        bid = ticker["bid"]
        ask = ticker["ask"]
        print "zaif_ask :" + str(ask)
        print "zaif_bid :" + str(bid)

        return ask, bid

    def ask(self, rate, amount):
        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': self.config["zaif"]["API_SECRET"]
        }
        data = {
            'nonce':  int(time.time()),
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "ask",
            "price": rate,
            "amount": amount
        }

        response = requests.post(self.baseURL + "tapi", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response

    def bid(self, rate, amount):
        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': self.config["zaif"]["API_SECRET"]
        }
        data = {
            'nonce':  int(time.time()),
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "bid",
            "price": rate,
            "amount": amount
        }

        response = requests.post(self.baseURL + "tapi", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))

        return response


if __name__ == '__main__':
    #api = ZaifAPI()
    #api.getTicker()
    pass
