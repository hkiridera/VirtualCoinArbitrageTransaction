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

        ## 値の取得に成功したらaskとbidを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200: 
            ticker = json.loads(response.text)
            bid = ticker["best_bid"]
            ask = ticker["best_ask"]
            print "bitflyer_ask :" + str(ask)
            print "bitflyer_bid :" + str(bid)
        else:
            ask = 99999999999999
            bid = -1

        return ask, bid

    def get_ticker_fx(self):
        """
        docstring
        """
        params = {"product_code": "FX_BTC_JPY"}
        #response = requests.get(self.base_url + "/v1/getticker", params=params)
        response = myutils.get(self.base_url + "/v1/getticker", params=params)

        ## 値の取得に成功したらaskとbidを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200: 
            ticker = json.loads(response.text)
            bid = ticker["best_bid"]
            ask = ticker["best_ask"]
            print "bitflyer_ask :" + str(ask)
            print "bitflyer_bid :" + str(bid)
        else:
            ask = 99999999999999
            bid = -1

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

        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Bitflyerで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
            return True
        return False

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
        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Bitflyerで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
            return True
        return False

    def ask_fx(self, rate, amount):
        """
        docstring
        """
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendchildorder"

        data = {
            "product_code": "FX_BTC_JPY",
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

        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Bitflyerで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
            return True
        return False

    def bid_fx(self, rate, amount):
        """
        Uncertain
        """
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendchildorder"
        
        data = {
            "product_code": "FX_BTC_JPY",
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
        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Bitflyerで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
            return True
        return False

    def scalping(self, amount):
        """
        Uncertain
        """

        # 現在価格取得
        ask, _ = self.get_ticker_fx()

        # 買う
        self.ask_fx(rate=int(ask - self.config["scalping"]), amount=amount)

        # 買えたか確認ループ
        while True:
            response = self.get_incomplete_orders_fx()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders == []:
                    break
        
        # 売る
        self.bid_fx(rate=int(ask + self.config["scalping"]), amount=amount)

        # 売れたか確認ループ
        while True:
            response = self.get_incomplete_orders_fx()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders == []:
                    break

        # 終了
        return True
    
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
        if response.status_code == 200:
            balance = json.loads(response.text)
            ## Analysis of response to json and confirmation of balance
            for resp in balance:
                if resp["currency_code"] == "JPY":
                    jpy = float(resp["amount"])
                elif resp["currency_code"] == "BTC":
                    btc = float(resp["amount"])

            print "bitflyer_amount jpy :" + str(jpy)
            print "bitflyer_amount btc :" + str(btc)
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
        #print orders
#        for resp in orders:
#            if resp["currency_code"] == "JPY":
#                jpy = resp["amount"]
#            elif resp["currency_code"] == "BTC":
#                btc = resp["amount"]
        return response

    def get_incomplete_orders_fx(self):
        """
        Uncertain 
        """

        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/getchildorders"
        params = {
            "child_order_state": "ACTIVE",
            "product_code": "FX_BTC_JPY"
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
        #print orders
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
            api.bid(rate=ask, amount=btc-0.001)

    def initialize_ask(self):
        '''
        開始前の初期購入
        足りなかったらamount分追加購入
        '''
        api = BitflyerAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
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
    #api.get_incomplete_orders_fx()

    #取引手数料
    #commissionrate = api.get_trading_commission()

    ## buy & sell BTC
    amount = 0.005
    #api.ask(rate=ask, amount=amount)
    #print amount
    #api.bid(rate=bid, amount=amount)

    # スキャルピング
    api.scalping(amount)