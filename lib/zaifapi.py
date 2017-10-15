# coding:utf-8
#!/usr/bin/env python
"""zaifのapiを実行する."""

import hmac
import hashlib
import json
import myutils
import sys
import signal
import time
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

        ## 値の取得に成功したらbuyとsellを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200:
            ticker = json.loads(response.text)
            sell = ticker["ask"]
            buy = ticker["bid"]
            print "zaif_buy :" + str(buy)
            print "zaif_sell :" + str(sell)
        else:
            buy = 99999999999999
            sell = -1

        return buy, sell

    def buy(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "buy",
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

        while True:
            #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
            response = myutils.post(self.base_url2, headers, data)
            if response.status_code == 200:
                ## send messege to slack
                myutils.post_slack(name="さやちゃん", text="Zaifで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
                return True

    def sell(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce2()
        
        data = {
            "method": "trade",
            "currency_pair": "btc_jpy",
            "action": "sell",
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

        while True:
            #response = requests.post(self.base_url + "tapi", headers=headers, data=data)
            response = myutils.post(self.base_url2, headers, data)

            if response.status_code == 200:
                ## send messege to slack
                myutils.post_slack(name="さやちゃん", text="Zaifで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
                return True

    def scalping(self, amount):
        """
        Uncertain
        """

        # 現在価格取得
        _, sell = self.get_ticker()

        # 買う
        self.sell(rate=int(sell - self.config["zaif"]["scalping"]), amount=amount)

        # 買えたか確認ループ
        i = 0
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["return"] == {}:
                    break
                elif i > 10:
                    self.cancel_all_order()
                    return
                else:
                    i += 1
                    time.sleep(0.5)
        
        # 売る
        self.buy(rate=int(sell), amount=amount)

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

    def IFD(self, amount, buy, sell):
        """
        Uncertain
        """

        # 現在価格取得
        _, sell = self.get_ticker()

        # 買う
        self.sell(rate=int(buy), amount=amount)

        # 買えたか確認ループ
        i = 0
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["return"] == {}:
                    break
                elif i > 10:
                    self.cancel_all_order()
                    return
                else:
                    i += 1
                    time.sleep(0.5)
        
        # 売る
        self.buy(rate=int(sell), amount=amount)

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

    def check_sell(self, amount=0):
        _, btc = self.get_balance()
        ## amount以上のbtcを持っている場合trueを返す
        if btc >= amount:
            return True
        else:
            return False

    def check_buy(self, amount=0):
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

    def all_sell(self):
        '''
        全部売る
        '''
        api = ZaifAPI()
        buy, sell = api.get_ticker()
        jpy, btc = api.get_balance()
        if float(btc) > 0.0:
            api.buy(rate=int(buy), amount=btc)

    def initialize_buy(self):
        '''
        開始前の初期購入
        '''
        api = ZaifAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
            buy, sell = self.get_ticker()
            # zaifはsell buyが逆
            #api.buy(rate=buy, amount=self.config["amount"])
            api.sell(rate=int(buy), amount=self.config["amount"])

if __name__ == '__main__':
    api = ZaifAPI()
    #buy, sell = api.get_ticker()
    #api.get_balance()

    #api.get_incomplete_orders()

    #初期btc購入
    #api.initialize_buy()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    api.all_sell()

    ## buy & sell BTC
    amount = 0.005
    #買う
    #api.sell(rate=int(sell), amount=amount)
    #売る
    #api.buy(rate=int(buy), amount=amount)
        
    # スキャルピング
    #api.scalping(amount)