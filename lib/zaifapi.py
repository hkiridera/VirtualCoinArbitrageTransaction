# coding:utf-8
#!/usr/bin/env python
"""zaifのapiを実行する."""

import hmac
import hashlib
import json
import myutils
import urllib
import yaml


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
        print data

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

        print data

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
        print response.text
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

    def cancel_all_order(self, ids):
        """
        Uncertain
        """

        response = {}
        for id in ids:
            nonce = myutils.nonce2()
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
    ask, bid = api.get_ticker()
    api.get_balance()

    api.get_incomplete_orders()

    ## buy & sell BTC
    amount = 0.005
    ## 5円区切り
    z_ask = int(ask * amount) + (5 - int(ask * amount) % 5 )
    z_bid = int(bid * amount) - ( int(bid * amount) % 5 )
    print z_ask, z_bid
    #api.ask(rate=int(ask), amount=amount)
    #api.bid(rate=int(bid), amount=amount)