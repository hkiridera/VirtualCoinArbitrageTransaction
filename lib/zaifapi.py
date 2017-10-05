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

        ## 値の取得に成功したらaskとbidを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200:
            ticker = json.loads(response.text)
            bid = ticker["bid"]
            ask = ticker["ask"]
            print "zaif_ask :" + str(ask)
            print "zaif_bid :" + str(bid)
        else:
            ask = 99999999999999
            bid = -1

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
        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Zaifで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
            return True

        return False

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

        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Zaifで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
            return True
        return False

    def scalping(self, amount):
        """
        Uncertain
        """

        # 現在価格取得
        _, bid = self.get_ticker()

        # 買う
        self.bid(rate=int(bid - self.config["zaif"]["scalping"]), amount=amount)

        # 買えたか確認ループ
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["return"] == {}:
                    break
        
        # 売る
        self.ask(rate=int(bid), amount=amount)

        # 売れたか確認ループ
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["return"] == {}:
                    break

        # 終了
        return True

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
        if response.status_code == 200:
            ticker = json.loads(response.text)
            jpy = float(ticker["return"]["funds"]["jpy"])
            btc = float(ticker["return"]["funds"]["btc"])

            print "zaif_amount jpy :" + str(jpy)
            print "zaif_amount btc :" + str(btc)
        else:
            jpy = 0
            btc = 0

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
        #print response.text
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

        ##空でない場合
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
        api = ZaifAPI()
        ask, bid = api.get_ticker()
        jpy, btc = api.get_balance()
        if float(btc) > 0.0:
            api.ask(rate=int(ask), amount=btc)

    def initialize_ask(self):
        '''
        開始前の初期購入
        '''
        api = ZaifAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
            ask, bid = self.get_ticker()
            # zaifはbid askが逆
            #api.ask(rate=ask, amount=self.config["amount"])
            api.bid(rate=int(ask), amount=self.config["amount"])

if __name__ == '__main__':
    api = ZaifAPI()
    #ask, bid = api.get_ticker()
    #api.get_balance()

    #api.get_incomplete_orders()

    #初期btc購入
    #api.initialize_ask()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    api.all_bid()

    ## buy & sell BTC
    amount = 0.005
    #買う
    #api.bid(rate=int(bid), amount=amount)
    #売る
    #api.ask(rate=int(ask), amount=amount)
        
    # スキャルピング
    #api.scalping(amount)