"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

import requests
import json
import yaml
import time
import hmac
import hashlib
import urllib
import base64
import myutils

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

        nonce = myutils.nonce()
        url_path = "tapi"
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "ask",
            "price": rate,
            "amount": amount
        }

        data['nonce'] = nonce,
        data["method"] = "trade"

        signature = self._signature(data=data)
        #message  = str(nonce) + url_path + urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response

    def bid(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce()
        url_path = "tapi"
        
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "bid",
            "price": rate,
            "amount": amount
        }

        data['nonce'] = nonce,
        data["method"] = "trade"

        signature = self._signature(data=data)
        #message  = str(nonce) + url_path + urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response

    def get_balance(self):
        """
        Uncertain
        """

        nonce = myutils.nonce()
        data = {}
        data['nonce'] = nonce,
        data["method"] = "get_info"
        

        signature = self._signature(data=data)
        #message  = urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url2, headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)

        ticker = json.loads(response.text)
        jpy = ticker["return"]["funds"]["jpy"]
        btc = ticker["return"]["funds"]["btc"]

        print "zaif_amount jpy :" + str(jpy)
        print "zaif_amount btc :" + str(btc)

        return jpy, btc

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

        nonce = myutils.nonce()
        data = {}
        data['nonce'] = nonce,
        data["method"] = "active_orders"
        

        signature = self._signature(data=data)
        #message  = urllib.urlencode(data)
        #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

        headers = {
            'key': self.config["zaif"]["ACCESS_KEY"],
            'sign': signature
        }

        #response = requests.post(self.base_url2, headers=headers, data=data)
        response = myutils.post(self.base_url2, headers, data)

        return response

    def cancel_all_order(self, ids):
        """
        Uncertain
        """

        response = {}
        for id in ids:
            nonce = myutils.nonce()
            data = {"order_id": id}
            data['nonce'] = nonce,
            data["method"] = "active_orders"
        
            signature = self._signature(data=data)
            #message  = urllib.urlencode(data)
            #signature = hmac.new(self.config["zaif"]["API_SECRET"], message, hashlib.sha512).hexdigest()

            headers = {
                'key': self.config["zaif"]["ACCESS_KEY"],
                'sign': signature
            }

            #response = requests.post(self.base_url2, headers=headers, data=data)
            response[id] = myutils.post(self.base_url2, headers, data)

        return response

if __name__ == '__main__':
    api = ZaifAPI()
    api.get_ticker()
    #api.get_balance()
    #pass
