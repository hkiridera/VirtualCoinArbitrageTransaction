# coding:utf-8
#!/usr/bin/env python
"""coincheckのapiを実行する."""

import hmac
import hashlib
import json
import myutils
import requests
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
        response = requests.get(self.base_url + "api/ticker")

        if response.status_code != 200:
            raise Exception('return status code is {}'.format(response.status_code))
        ticker = json.loads(response.text)
        bid = ticker["bid"]
        ask = ticker["ask"]

        print "coincheck_ask :" + str(ask)
        print "coincheck_bid :" + str(bid)

        return ask, bid

    def ask(self, rate=0, amount=0):
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

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)

        ## send messege to slack
        myutils.post_slack(name="coincheck", text="ask : btc=" + amount + " jpy=" + rate)
        
        return response


    def bid(self, rate, amount):
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

        #response = requests.post(self.base_url + url_path, headers=headers, data=data)
        response = myutils.post(self.base_url + url_path, headers, data)
        
        ## send messege to slack
        myutils.post_slack(name="coincheck", text="bid : btc=" + amount + " jpy=" + rate)
        return response


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

        ticker = json.loads(response.text)
        jpy = float(ticker["jpy"])
        btc = float(ticker["btc"])

        print "coincheck_amount jpy :" + str(jpy)
        print "coincheck_amount btc :" + str(btc)

        return jpy, btc

    def check_bid(self, amount=0):
        _, btc = self.get_balance()
        print btc
        print amount

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
        print ticker
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
        api = CoincheckAPI()
        ask, bid = self.get_ticker()
        api.ask(rate=ask, amount=self.config["amount"])

if __name__ == '__main__':
    api = CoincheckAPI()
    ask, bid = api.get_ticker()
    api.get_balance()
    
    #初期btc購入
    #api.initialize_ask()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    #api.all_bid()

    # 未確定オーダー
    #api.get_incomplete_orders()

    ## buy & sell BTC
    amount = 0.005
    #api.ask(rate=ask, amount=amount)
    #api.bid(rate=bid, amount=amount)
    #pass

    print api.check_bid(amount=amount)
