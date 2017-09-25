# coding:utf-8
#!/usr/bin/env python
"""zaifのapiを実行する."""

import hmac
import hashlib
import json
import myutils
import sys
import signal
import urllib
import yaml

from time import sleep

def handler(signal, frame):
    """
    強制終了用ハンドラ
    ctl + cで止まる
    """
    print('うおおお、やられたーー')
    sys.exit(0)
signal.signal(signal.SIGINT, handler)

class ZaifAPI():
    """
    docstring
    """

    def __init__(self):
        self.base_url = "https://api.zaif.jp/api/1/"
        self.base_url2 = "https://api.zaif.jp/tapi"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def get_ticker(self):
        """
        docstring
        """
        url_path = "ticker/btc_jpy"
        #response = requests.get(self.base_url + "ticker/btc_jpy")
        response = myutils.get(self.base_url + url_path)

        ticker = json.loads(response.text)
        bid = ticker["bid"]
        ask = ticker["ask"]
        print "zaif_ask :" + str(ask)
        print "zaif_bid :" + str(bid)

        return ask, bid

    def ask(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "ask",
            "price": rate,
            "amount": amount,

            'nonce': nonce,
            "method": "trade"
        }

        signature = self._signature(data=data)
        #message  = str(nonce) + url_path + urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)

        print response.text
        return response

    def bid(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "bid",
            "price": rate,
            "amount": amount,

            'nonce': nonce,
            "method": "trade"
        }

        signature = self._signature(data=data)
        #message  = str(nonce) + url_path + urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)

        print response.text
        return response

    def get_balance(self):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        data = {
            'nonce': nonce,
            "method": "get_info"
        }
        
        signature = self._signature(data=data)
        #message  = urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url2, headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)
        if response is None:
            ticker = json.loads(response.text)
            jpy = ticker["return"]["funds"]["jpy"]
            btc = ticker["return"]["funds"]["btc"]

            print "zaif_amount jpy :" + str(jpy)
            print "zaif_amount btc :" + str(btc)

            return jpy, btc

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

    def _signature(self, data=None):
        """
        docstring
        """
        _message  = urllib.urlencode(data)
        _signature = hmac.new(self.config["zaif"]["API_SECRET"], _message, hashlib.sha512).hexdigest()

        return _signature

    def get_incomplete_orders(self):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        data = {
            'nonce': nonce,
            "method": "active_orders"
        }
        

        signature = self._signature(data=data)
        #message  = urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        
        #response = requests.post(self.base_url2, headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)
        print response.text

        return response

    def cancel_order(self, id):
        """
        Uncertain
        """

        response = {}
        nonce = myutils.nonce2()
        data = {
            'nonce': nonce,
            "method": "cancel_order",
            "order_id": id
        }
        
        signature = self._signature(data=data)
        #message  = urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url2, headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)

        print response.text
        return response

    def cancel_all_order(self):
        ## all orders canncelled
        api = ZaifAPI()
        resp = api.get_incomplete_orders()
        orders = json.loads(resp.text)

        ##空の場合
        if orders["return"] != {}:
            print orders["return"]
            for order in orders["return"]:
                print order
                api.cancel_order(id=str(order))

        return True

    def all_bid(self):
        '''
        全部売る
        '''
        ask, bid = self.get_ticker()
        jpy, btc = self.get_balance()
        if float(btc) > 0.0:
            api.ask(rate=int(ask), amount=btc)

    def initialize_ask(self):
        '''
        開始前の初期購入
        '''
        api = ZaifAPI()
        ask, bid = self.get_ticker()
        api.bid(rate=int(bid), amount=self.config["amount"])

if __name__ == '__main__':
    api = ZaifAPI()
    ask, bid = api.get_ticker()
    api.get_balance()

    #api.get_incomplete_orders()

    #初期btc購入
    #api.initialize_ask()

    ## all orders canncelled
    api.cancel_all_order()

    # 全売却
    api.all_bid()

    ## buy & sell BTC
    #amount = 0.005
    #買う
    #api.bid(rate=int(bid), amount=amount)
    #売る
    #api.ask(rate=int(ask), amount=amount)
        