# coding:utf-8
#!/usr/bin/env python
"""coincheckのapiを実行する."""

import hmac
import hashlib
import json
import myutils
import requests
import time
import urllib
import yaml

class CoincheckAPI():
    """
    docstring
    """
    def __init__(self):
        self.base_url = "https://coincheck.com/"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

    def get_ticker(self):
        """
        docstring
        """
        #payload = {'pair': 'XXBTZJPY'}

        while True:
            response = myutils.get(self.base_url + "api/ticker")

            ## 値の取得に成功したらbuyとsellを返す
            ## 失敗したら変な値を返す
            if response.status_code == 200: 
                ticker = json.loads(response.text)
                sell = ticker["ask"]
                buy = ticker["bid"]
                print "coincheck_buy :" + str(buy)
                print "coincheck_sell :" + str(sell)
                return buy, sell

    def buy(self, rate=0, amount=0):
        """
        Uncertain
        """

        nonce = myutils.nonce()
        url_path = "api/exchange/orders"

        '''
        data = {
            "market_buy_amount": amount,
            "order_type": "market_buy",
            "pair": "btc_jpy"
        }
        '''
        data = {
            "rate": rate,
            "amount": amount,
            "order_type": "buy",
            "pair": "btc_jpy"
        }
        
        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = str(nonce) + url
        #signature = hmac.new(self.config["coincheck"]["API_SECRET"], message, hashlib.sha256).hexdigest()

        headers = {
            'ACCESS-KEY': self.config["coincheck"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }

        while True:
            #response = requests.post(self.base_url + url_path, headers=headers, data=data)
            response = myutils.post(self.base_url + url_path, headers, data)

            if response.status_code == 200:
                ## send messege to slack
                myutils.post_slack(name="さやちゃん", text="Coincheckで" + str(amount) + "BTCを" + str(rate) + "で買っといたよ")
                return True

    def sell(self, rate, amount):
        """
        Uncertain
        """

        nonce = myutils.nonce()
        url_path = "api/exchange/orders"

        '''
        data = {
            "market_sell_amount": amount,
            "order_type": "market_sell",
            "pair": "btc_jpy"
        }
        '''
        
        data = {
            "rate": rate,
            "amount": amount,
            "order_type": "sell",
            "pair": "btc_jpy"
        }

        signature = self._signature(nonce=nonce, url_path=url_path, data=data)
        #message  = str(nonce) + url + data
        #signature = hmac.new(self.config["coincheck"]["API_SECRET"], message, hashlib.sha256).hexdigest()
 
        headers = {
            'ACCESS-KEY': self.config["coincheck"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }

        while True:
            #response = requests.post(self.base_url + url_path, headers=headers, data=data)
            response = myutils.post(self.base_url + url_path, headers, data)
            if response.status_code == 200:
                ## send messege to slack
                myutils.post_slack(name="さやちゃん", text="Coincheckで" + str(amount) + "BTCを" + str(rate) + "で売っといたよ")
                return True

    def scalping(self, amount):
        """
        Uncertain
        """

        # 現在価格取得
        buy, _ = self.get_ticker()

        # 買う
        self.buy(rate=int(buy - self.config["coincheck"]["scalping"]), amount=amount)

        # 買えたか確認ループ
        i = 0
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["orders"] == []:
                    break
                elif i > 120:
                    self.cancel_all_order()
                    return
                else:
                    i += 1
                    time.sleep(0.5)
        
        # 売る
        self.sell(rate=int(buy), amount=amount)

        # 売れたか確認ループ
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["orders"] == []:
                    break
                else:
                    time.sleep(0.5)

        # 終了
        return True

    def IFD(self, amount, buy, sell):
        """
        Uncertain
        """

        # 買う
        self.buy(rate=int(buy), amount=amount)

        # 買えたか確認ループ
        i = 0
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["orders"] == []:
                    break
                elif i > 120:
                    self.cancel_all_order()
                    return
                else:
                    i += 1
                    time.sleep(0.5)
        
        # 売る
        self.sell(rate=int(sell), amount=amount)

        # 売れたか確認ループ
        while True:
            response = self.get_incomplete_orders()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空でない場合
                if orders["orders"] == []:
                    break
                else:
                    time.sleep(0.5)

        # 終了
        return True

    def get_balance(self):
        """
        docstring
        return jpy, btc
        """

        nonce = myutils.nonce()
        url_path = "api/accounts/balance"

        #message  = str(nonce) + url
        #signature = hmac.new(self.config["coincheck"]["API_SECRET"], message, hashlib.sha256).hexdigest()
        signature = self._signature(nonce=nonce, url_path=url_path)
        headers = {
            'ACCESS-KEY': self.config["coincheck"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }
        #response = requests.get(self.base_url + url_path , headers=headers)
        response = myutils.get(self.base_url + url_path, headers)

        if response.status_code == 200:
            ticker = json.loads(response.text)
            jpy = float(ticker["jpy"])
            btc = float(ticker["btc"])

            print "coincheck_amount jpy :" + str(jpy)
            print "coincheck_amount btc :" + str(btc)
        else:
            jpy = 0
            btc = 0

        return jpy, btc

    def check_sell(self, amount=0):
        _, btc = self.get_balance()
        print btc
        print amount

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
        if data == None:
            _message = str(nonce) + (self.base_url + url_path)
        else:    
            body = urllib.urlencode(data)
            _message = str(nonce) + (self.base_url + url_path) + body
        _signature = hmac.new(self.config["coincheck"]["API_SECRET"], _message, hashlib.sha256).hexdigest()
        
        return _signature

    def get_incomplete_orders(self):
        """
        docstring
        """

        nonce = myutils.nonce()
        url_path = "api/exchange/orders/opens"
        signature = self._signature(nonce=nonce, url_path=url_path)
        headers = {
            'ACCESS-KEY': self.config["coincheck"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }
        #response = requests.get(self.base_url + url_path , headers=headers)
        response = myutils.get(self.base_url + url_path, headers)
        ticker = json.loads(response.text)
        #print ticker
        return response

    def cancel_order(self, id=None):
        """
        docstring
        """
        if id == None:
            return False

        nonce = myutils.nonce()
        url_path = "api/exchange/orders/" + id 

        #message  = str(nonce) + url
        #signature = hmac.new(self.config["coincheck"]["API_SECRET"], message, hashlib.sha256).hexdigest()
        signature = self._signature(nonce=nonce, url_path=url_path)
        headers = {
            'ACCESS-KEY': self.config["coincheck"]["ACCESS_KEY"],
            'ACCESS-SIGNATURE': signature,
            'ACCESS-NONCE': nonce
        }

        response = myutils.delete(self.base_url + url_path, headers)

        ticker = json.loads(response.text)
        print ticker

        return response

    def cancel_all_order(self):
        ## all orders canncelled
        api = CoincheckAPI()
        resp = api.get_incomplete_orders()
        orders = json.loads(resp.text)

        for order in orders["orders"]:
            print order["id"]
            api.cancel_order(str(order["id"]))

        return True

    def all_sell(self):
        '''
        全部売る
        '''
        buy, sell = self.get_ticker()
        jpy, btc = self.get_balance()
        if float(btc) > 0.0:
            api.sell(rate=buy, amount=btc)

    def initialize_buy(self):
        '''
        開始前の初期購入
        '''
        api = CoincheckAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
            buy, sell = self.get_ticker()
            api.buy(rate=buy, amount=self.config["amount"])

if __name__ == '__main__':
    api = CoincheckAPI()
    #buy, sell = api.get_ticker()
    #api.get_balance()
    
    #初期btc購入
    #api.initialize_buy()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    api.all_sell()

    # 未確定オーダー
    #api.get_incomplete_orders()

    ## buy & sell BTC
    amount = 0.005
    #api.buy(rate=buy, amount=amount)
    #api.sell(rate=sell, amount=amount)
    #pass

    #print api.check_sell(amount=amount)

    # スキャルピング
    #api.scalping(amount)