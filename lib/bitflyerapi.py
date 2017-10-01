# coding:utf-8
#!/usr/bin/env python
"""bitflyerのapiを実行する."""

import hashlib
import hmac
import json
import myutils
import urllib
import requests
import yaml


class BitflyerAPI():
    """
    docstring
    """

    def __init__(self):
        self.base_url = "https://api.bitflyer.jp"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def get_ticker(self):
        """
        docstring
        """
        params = {"product_code": "BTC_JPY"}
        #response = requests.get(self.base_url + "/v1/getticker", params=params)
        response = myutils.get(self.base_url + "/v1/getticker", params=params)
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
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendchildorder"

        data = {
            "product_code": "BTC_JPY",
            "child_order_type": "LIMIT",
            "side": "BUY",
            "price": rate,
            "size": amount
        }

        signature = self._signature(nonce=nonce, method="POST", url_path=url_path, data=data)

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(url=self.base_url + url_path, headers=headers, data=json.dumps(data))


        ## send messege to slack
        myutils.post_slack(name="さやちゃん", text="Bitflyerで" + amount + "BTCを" + rate + "で買っといたよ")
        return response

    def bid(self, rate, amount):
        """
        Uncertain
        """
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendchildorder"
        
        data = {
            "product_code": "BTC_JPY",
            "child_order_type": "LIMIT",
            "side": "SELL",
            "price": rate,
            "size": amount
        }

        signature = self._signature(nonce=nonce, method="POST", url_path=url_path, data=data)

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(url=self.base_url + url_path, headers=headers, data=json.dumps(data))

        ## send messege to slack
        myutils.post_slack(name="さやちゃん", text="Bitflyerで" + amount + "BTCを" + rate + "で売っといたよ")
        return response

    def get_balance(self):
        """
        Uncertain 
        return jpy, btc
        """

        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/getbalance"
        
        signature = self._signature(nonce=nonce, method="GET", url_path=url_path)
        #message  = nonce + "get" + url_path
        #signature = hmac.new(self.config["bitflyer"]["API_SECRET"], message, hashlib.sha256).hexdigest()

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        #response = requests.get(url + url_path, headers=headers)
        response = myutils.get(url=self.base_url + url_path, headers=headers)
        balance = json.loads(response.text)
        ## Analysis of response to json and confirmation of balance

        for resp in balance:
            if resp["currency_code"] == "JPY":
                jpy = float(resp["amount"])
            elif resp["currency_code"] == "BTC":
                btc = float(resp["amount"])

        print "bitflyer_amount jpy :" + str(jpy)
        print "bitflyer_amount btc :" + str(btc)

        return jpy, btc


    def check_bid(self, amount=0):
        _, btc = self.get_balance()
        ## amount以上のbtcを持っている場合trueを返す
        if btc >= amount:
            return True
        else:
            return False

    def check_ask(self, amount=0):
        jpy, _ = self.get_balance()
        ## amount以上の円を持っている場合trueを返す
        if jpy >= amount:
            return True
        else:
            return False

    def _signature(self, nonce=None, method="GET", url_path=None, params=None, data=None):
        """
        docstring
        """

        if data is not None:
            _message  = str.encode(str(nonce) + method + url_path + json.dumps(data))
        elif params is not None:
            _message  = str.encode(str(nonce) + method + url_path + params)
        else:
            _message  = str.encode(str(nonce) + method + url_path)
        

        _signature = hmac.new(self.config["bitflyer"]["API_SECRET"], _message, hashlib.sha256).hexdigest()

        return _signature

    def get_incomplete_orders(self):
        """
        Uncertain 
        """

        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/getchildorders"
        params = {
            "child_order_state": "ACTIVE",
            "product_code": "BTC_JPY"
            }
        
        signature = self._signature(nonce=nonce, method="GET", url_path=url_path, params="?"+urllib.urlencode(params))
        #message  = nonce + "get" + url_path
        #signature = hmac.new(self.config["bitflyer"]["API_SECRET"], message, hashlib.sha256).hexdigest()

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        #response = requests.get(url + url_path, headers=headers)
        response = myutils.get(url=self.base_url + url_path, headers=headers, params=params)
        orders = json.loads(response.text)
        print orders
#        for resp in orders:
#            if resp["currency_code"] == "JPY":
#                jpy = resp["amount"]
#            elif resp["currency_code"] == "BTC":
#                btc = resp["amount"]
        return response

    def cancel_all_order(self):
        """
        docstring
        """

        nonce = myutils.nonce2()
        url_path = "/v1/me/cancelallchildorders"

        data = {
            "product_code": "BTC_JPY"
        }

        #message  = str(nonce) + url
        #signature = hmac.new(self.config["coincheck"]["API_SECRET"], message, hashlib.sha256).hexdigest()
        signature = self._signature(nonce=nonce, method="POST", url_path=url_path, data=data)
        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        response = myutils.post(url=self.base_url + url_path, headers=headers, data=json.dumps(data))

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

    def get_trading_commission(self):
        """
        Uncertain 
        """

        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/gettradingcommission"

        params = {
            "product_code": "BTC_JPY"
        }

        signature = self._signature(nonce=nonce, method="GET", url_path=url_path, params="?"+urllib.urlencode(params))

        headers = {
            'ACCESS-KEY': self.config["bitflyer"]["ACCESS_KEY"],
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': nonce,
            "Content-Type": "application/json"
        }

        #response = requests.get(url + url_path, headers=headers)
        response = myutils.get(url=self.base_url + url_path, headers=headers, params=params)
        commission = json.loads(response.text)
        print "bitfyer commission_rate : " + str(commission["commission_rate"])

        return commission["commission_rate"]        

if __name__ == '__main__':
    api = BitflyerAPI()
    ask, bid = api.get_ticker()
    api.get_balance()
    #pass


    #初期btc購入
    #api.initialize_ask()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    #api.all_bid()

    # 未確定オーダー
    #api.get_incomplete_orders()

    #取引手数料
    commissionrate = api.get_trading_commission()

    ## buy & sell BTC
    amount = 0.005
    #api.ask(rate=ask, amount=amount)
    #print amount
    #api.bid(rate=bid, amount=amount)
