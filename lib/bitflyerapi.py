# coding:utf-8
#!/usr/bin/env python
"""bitflyerのapiを実行する."""

import hashlib
import hmac
import json
import myutils
import requests
import yaml


class BitflyerAPI():
    """
    docstring
    """

    def __init__(self):
        self.base_url = "https://api.bitflyer.jp/v1/"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def get_ticker(self):
        """
        docstring
        """
        params = {"product_code": "BTC_JPY"}
        response = requests.get(self.base_url + "getticker", params=params)
        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ticker = json.loads(response.text)
        bid = ticker["best_bid"]
        ask = ticker["best_ask"]
        print "bitflyer_ask :" + str(ask)
        print "bitflyer_bid :" + str(bid)

        return ask, bid

    def ask(self, rate, amount):
        """
        docstring
        """
        nonce = myutils.nonce()
        url = self.base_url
        url_path = "me/sendchildorder"

        data = {
            "product_code": "BTC_JPY",
            "child_order_type": "MARKEY",
            "side": "BUY",
            #"price": rate,
            "size": amount,
            #"minute_to_expire": 10000,
            "time_in_force": "GTC"
        }

        signature = self._signature(nonce=nonce, method="post", url_path=url_path, data=data)

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response

    def bid(self, rate, amount):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url = self.base_url
        url_path = "me/sendchildorder"
        
        data = {
            "product_code": "BTC_JPY",
            "child_order_type": "MARKEY",
            "side": "SELL",
            #"price": rate,
            "size": amount,
            #"minute_to_expire": 10000,
            "time_in_force": "GTC"
        }

        signature = self._signature(nonce=nonce, method="post", url_path=url_path, data=data)

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response

    def get_balance(self):
        """
        Uncertain 
        return jpy, btc
        """

        nonce = myutils.nonce()
        url = self.base_url
        url_path = "/me/getbalance"
        
        signature = self._signature(nonce=nonce, method="get", url_path=url_path)
        #message  = nonce + "get" + url_path
        #signature = hmac.new(self.config["bitflyer"]["API_SECRET"], message, hashlib.sha256).hexdigest()

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce
        }

        #response = requests.get(url + url_path, headers=headers)
        response = myutils.get(self.base_url + url_path, headers)
        

        ## Analysis of response to json and confirmation of balance
        '''
        for resp in response.text:
            if resp["currency_code"] == "JPY":
                jpy = resp["amount"]
            elif resp["currency_code"] == "BTC":
                btc = resp["amount"]

        print "bitflyer_amount jpy :" + str(jpy)
        print "bitflyer_amount btc :" + str(btc)

        return jpy, btc
        '''

    def check_bid(self, amount=0):
        _, btc = self.get_balance()
        ## amount以上のbtcを持っている場合trueを返す
        if btc > amount:
            return True
        else:
            return False

    def check_ask(self, amount=0):
        jpy, _ = self.get_balance()
        ## amount以上の円を持っている場合trueを返す
        if jpy > amount:
            return True
        else:
            return False

    def _signature(self, nonce=None, method="get", url_path=None, data=None):
        """
        docstring
        """
        
        if data == None:
            _message  = str.encode(str(nonce) + method + url_path)
        else:
            _message  = str.encode(str(nonce) + method + url_path + data)
        _signature = hmac.new(self.config["bitflyer"]["API_SECRET"], _message, hashlib.sha256).hexdigest()

        return _signature

    def get_incomplete_orders(self):
        """
        Uncertain 
        """

        nonce = myutils.nonce()
        url = self.base_url
        url_path = "/me/getchildorders"
        
        signature = self._signature(nonce=nonce, method="get", url_path=url_path)
        #message  = nonce + "get" + url_path
        #signature = hmac.new(self.config["bitflyer"]["API_SECRET"], message, hashlib.sha256).hexdigest()

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce
        }

        #response = requests.get(url + url_path, headers=headers)
        response = myutils.get(self.base_url + url_path, headers)

        return response

    def cancel_all_order(self):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url = self.base_url
        url_path = "me/cancelallchildorders"
        
        data = {
            "product_code": "BTC_JPY"
        }

        signature = self._signature(nonce=nonce, method="post", url_path=url_path, data=data)

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response

    def all_bid(self):
        '''
        全部売る
        '''
        ask, bid = self.get_ticker()
        jpy, btc = self.get_balance()
        if float(btc) > 0.0:
            api.bid(rate=ask, amount=btc)

    def initialize_ask(self):
        '''
        開始前の初期購入
        '''
        api = BitflyerAPI()
        ask, bid = self.get_ticker()
        api.ask(rate=ask, amount=self.config["amount"])

if __name__ == '__main__':
    api = BitflyerAPI()
    api.get_ticker()
    api.get_balance()
    #pass
