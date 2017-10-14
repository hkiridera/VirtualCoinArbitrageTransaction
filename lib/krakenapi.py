# coding:utf-8
#!/usr/bin/env python
"""krakenのapiを実行する."""

import base64
import hmac
import hashlib
import json
import myutils
import requests
import time
import urllib
import yaml


class krakenfAPI():
    """
    docstring
    """

    def __init__(self):
        self.base_url = "https://api.kraken.com"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)


    def get_ticker(self):
        """
        docstring
        """
        params = {'pair': 'XXBTZJPY'}
        #response = requests.get(self.base_url + "/0/public/Ticker", params=params)
        response = myutils.get(self.base_url + "/0/public/Ticker", params=params)

        ## 値の取得に成功したらbuyとsellを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200: 
            ticker = json.loads(response.text)
            sell = float(ticker["result"]["XXBTZJPY"]["b"][0])
            buy = float(ticker["result"]["XXBTZJPY"]["a"][0])
            print "kraken_buy :" + str(buy)
            print "kraken_sell :" + str(sell)
        else:
            buy = 99999999999999
            sell = -1

        return buy, sell

    def buy(self, rate, amount):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url_path = "/0/private/AddOrder"

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

        data["nonce"] = nonce

        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
        #signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), message, hashlib.sha512)

        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)
        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Krakenで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
            return True

        return False


    def sell(self, rate, amount):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url_path = "/0/private/AddOrder"
        
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

        data["nonce"] = nonce

        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
        #signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), message, hashlib.sha512)

        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }

        #response = requests.get(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        if response.status_code == 200:
            ## send messege to slack
            myutils.post_slack(name="さやちゃん", text="Krakenで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
            return True

        return False

    def scalping(self, amount):
        """
        Uncertain
        """

        # 現在価格取得
        buy, _ = self.get_ticker()

        # 買う
        self.buy(rate=int(buy - self.config["kraken"]["scalping"]), amount=amount)

        # 買えたか確認ループ
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["return"] == {}:
                    break
        
        # 売る
        self.sell(rate=int(buy), amount=amount)

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

    def get_barance(self):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url_path = "/0/private/Balance"

        data = {}
        data["nonce"] = nonce

        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
        #signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), message, hashlib.sha512)

        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'API-Sign': base64.b64encode(signature.digest())
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)
        if response.status_code == 200:
            ticker = json.loads(response.text)
            print ticker
            #jpy = float(ticker["jpy"])
            #btc = float(ticker["btc"])

            #print "coincheck_amount jpy :" + str(jpy)
            #print "coincheck_amount btc :" + str(btc)
        #else:
            #jpy = 0
            #btc = 0

        #return jpy, btc

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

    def _signature(self, nonce=None, url_path=None, data=None):
        """
        docstring
        """
        _message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
        _signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), _message, hashlib.sha512)

        return _signature

    def get_incomplete_orders(self):
        """
        Uncertain
        """
        nonce = myutils.nonce()
        url_path = "/0/private/OpenOrders"

        data = {}
        data["nonce"] = nonce

        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
        #signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), message, hashlib.sha512)

        headers = {
            'API-Key': self.config["kraken"]["ACCESS_KEY"],
            'API-Sign': base64.b64encode(signature.digest())
        }

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        return response
        
    def cancel_all_order(self,ids):
        """
        Uncertain
        """

        response = {}
        for id in ids:
            nonce = myutils.nonce()
            url_path = "/0/private/CancelOrder"

            data = {"txid": id}
            data["nonce"] = nonce

            signature = self._signature(nonce=nonce, url_path=url_path, data=data)
            #message  = url_path + hashlib.sha256(str(nonce) +  urllib.urlencode(data)).digest()
            #signature = hmac.new(base64.b64decode(self.config["kraken"]["API_SECRET"]), message, hashlib.sha512)

            headers = {
                'API-Key': self.config["kraken"]["ACCESS_KEY"],
                'API-Sign': base64.b64encode(signature.digest())
            }

            #response = requests.post(self.base_url + url_path, headers=headers, data=data)
            response[id] = myutils.post(self.base_url + url_path, headers, data)

        return response

    def all_sell(self):
        '''
        全部売る
        '''
        api = krakenfAPI()
        buy, sell = api.get_ticker()
        jpy, btc = api.get_balance()
        if float(btc) > 0.0:
            api.sell(rate=buy, amount=btc)

    def initialize_buy(self):
        '''
        開始前の初期購入
        '''
        api = krakenfAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
            buy, sell = self.get_ticker()
            api.buy(rate=buy, amount=self.config["amount"])


if __name__ == '__main__':
    api = krakenfAPI()
    api.get_ticker()
    api.get_barance()
    #pass
