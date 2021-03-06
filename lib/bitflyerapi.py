# coding:utf-8
#!/usr/bin/env python
"""bitflyerのapiを実行する."""

import hashlib
import hmac
import json
import multiprocessing
import myutils
import time
import threading
import urllib
import requests
import yaml

from tornado import gen
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_tornado import PubNubTornado
from pubnub.pnconfiguration import PNReconnectionPolicy

config = PNConfiguration()
config.subscribe_key = 'sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f'
config.reconnect_policy = PNReconnectionPolicy.LINEAR
pubnub = PubNubTornado(config)

sell_s = -1
buy_s = -1

f = open('b_ticker.csv', 'a')

class BitflyerAPI():
    """
    docstring
    """

    def __init__(self):
        self.base_url = "https://api.bitflyer.jp"
        with open('config.yml', 'r') as yml:
            self.config = yaml.load(yml)

        # False = down , True = up
        self.up_or_down = False

    def get_ticker(self):
        """
        docstring
        """
        params = {"product_code": "BTC_JPY"}

        while True:
            #response = requests.get(self.base_url + "/v1/getticker", params=params)
            response = myutils.get(self.base_url + "/v1/getticker", params=params)

            ## 値の取得に成功したらbuyとsellを返す
            ## 失敗したら変な値を返す
            if response.status_code == 200:
                ticker = json.loads(response.text)
                sell = ticker["best_bid"]
                buy = ticker["best_ask"]
                print "bitflyer_buy :" + str(buy)
                print "bitflyer_sell :" + str(sell)
                return buy, sell

    @gen.coroutine
    def _get_ticker_streaming(self):
        class BitflyerSubscriberCallback(SubscribeCallback):
            def presence(self, pubnub, presence):
                pass  # handle incoming presence data

            def status(self, pubnub, status):
                if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                    pass  # This event happens when radio / connectivity is lost

                elif status.category == PNStatusCategory.PNConnectedCategory:
                    # Connect event. You can do stuff like publish, and know you'll get it.
                    # Or just use the connected event to confirm you are subscribed for
                    # UI / internal notifications, etc
                    pass
                elif status.category == PNStatusCategory.PNReconnectedCategory:
                    pass
                    # Happens as part of our regular operation. This event happens when
                    # radio / connectivity is lost, then regained.
                elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
                    pass
                    # Handle message decryption error. Probably client configured to
                    # encrypt messages and on live data feed it received plain text.

            def message(self, pubnub, message):
                # Handle new message stored in message.message
                # メインの処理はここで書きます
                # 登録したチャンネルからメッセージ(価格の変化など)がくるたび、この関数が呼ばれます

                #print("%s : %s" % (message.channel, message.message))
                #ticker = json.loads(message.message)
                global sell_s,buy_s
                sell_s = message.message["best_sell"]
                buy_s = message.message["best_buy"]
                #print sell_s, buy_s

                f.write(time.time() + ",sell,buy," + str(sell_s) + "," + str(buy_s) +"\n")

        listener = BitflyerSubscriberCallback()
        pubnub.add_listener(listener)
        pubnub.subscribe().channels("lightning_ticker_FX_BTC_JPY").execute()
        pubnub.start()

    def get_ticker_streaming(self):
        th1 = threading.Thread(target=self._get_ticker_streaming)
        th1.setDaemon(True)
        th1.start()

    def get_ticker_fx(self):
        """
        docstring
        """
        params = {"product_code": "FX_BTC_JPY"}
        #response = requests.get(self.base_url + "/v1/getticker", params=params)
        response = myutils.get(self.base_url + "/v1/getticker", params=params)

        ## 値の取得に成功したらbuyとsellを返す
        ## 失敗したら変な値を返す
        if response.status_code == 200: 
            ticker = json.loads(response.text)
            sell = ticker["best_ask"]
            buy = ticker["best_bid"]
            print "bitflyer_buy :" + str(buy)
            print "bitflyer_sell :" + str(sell)
        else:
            buy = 99999999999999
            sell = -1

        return buy, sell

    def buy(self, rate, amount):
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

    def sell(self, rate, amount):
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

    def IFDOCO(self, rate, amount):
        """
        docstring
        """
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendparentorder"

        data = {
            "order_method": "IFDOCO",
            "minute_to_expire": self.config["bitflyer"]["minute_to_expire"],
            "time_in_force": "GTC",
            "parameters": [{
                "product_code": "FX_BTC_JPY",
                "condition_type": "LIMIT",
                "side": "BUY",
                "price": rate,
                "size": amount
            },
            {
                "product_code": "FX_BTC_JPY",
                "condition_type": "LIMIT",
                "side": "SELL",
                "price": rate + self.config["bitflyer"]["scalping"],
                "size": amount
            },
            {
                "product_code": "FX_BTC_JPY",
                "condition_type": "STOP_LIMIT",
                "side": "SELL",
                "price": rate - self.config["bitflyer"]["trigger_price"],
                "trigger_price": rate - self.config["bitflyer"]["trigger_price"],
                "size": amount
            }]
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

    def IFD(self, amount, buy, sell):
        """
        docstring
        """
        nonce = myutils.nonce2()
        url = self.base_url
        url_path = "/v1/me/sendparentorder"

        data = {
            "order_method": "IFD",
            "minute_to_expire": self.config["bitflyer"]["minute_to_expire"],
            "time_in_force": "GTC",
            "parameters": [{
                "product_code": "FX_BTC_JPY",
                "condition_type": "LIMIT",
                "side": "BUY",
                "price": buy,
                "size": amount
            },
            {
                "product_code": "FX_BTC_JPY",
                "condition_type": "LIMIT",
                "side": "SELL",
                "price": sell,
                "size": amount
            }]
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

    def buy_fx(self, rate, amount):
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

    def sell_fx(self, rate, amount):
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
        #buy, _ = self.get_ticker_fx()

        # 買う
        self.buy_fx(rate=int(buy_s - self.config["bitflyer"]["scalping"]), amount=amount)
        # 売買できたか確認ループ
        i = 0
        while True:
            # 1分間買えなかった場合キャンセルする
            if i > 10:
                self.cancel_all_order_fx()
                return
            response = self.get_incomplete_orders_fx()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空の場合
                if orders == []:
                    break
                else:
                    # API制限のため少し待つ
                    i += 1
                    time.sleep(0.5)

        # 売る
        self.sell_fx(rate=int(buy_s), amount=amount)
        # 売買できたか確認ループ
        while True:
            response = self.get_incomplete_orders_fx()
            if response.status_code == 200:
                orders = json.loads(response.text)
                ##空の場合
                if orders == []:
                    break
                else:
                    # API制限のため少し待つ
                    time.sleep(0.5)
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
        if response.status_code == 200:
            orders = json.loads(response.text)
            #print orders
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

        return True

    def cancel_all_order_fx(self):
        """
        docstring
        """

        nonce = myutils.nonce2()
        url_path = "/v1/me/cancelallchildorders"

        data = {
            "product_code": "FX_BTC_JPY"
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

        return True

    def all_sell(self):
        '''
        全部売る
        '''
        buy, sell = self.get_ticker()
        jpy, btc = self.get_balance()
        if float(btc) > 0.0:
            api.sell(rate=buy, amount=btc-0.001)

    def initialize_buy(self):
        '''
        開始前の初期購入
        足りなかったらamount分追加購入
        '''
        api = BitflyerAPI()
        jpy, btc = api.get_balance()
        if self.config["amount"] > btc:
            buy, sell = self.get_ticker()
            api.buy(rate=buy, amount=self.config["amount"])

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

    def up_or_down(self):
        '''
        1分前のデータと比較して、今は上昇傾向なのか下降傾向なのかを判定する
        '''
        pass

if __name__ == '__main__':
    api = BitflyerAPI()
    #buy, sell = api.get_ticker()
    #api.get_balance()
    #pass


    #初期btc購入
    #api.initialize_buy()

    ## all orders canncelled
    #api.cancel_all_order()

    # 全売却
    api.all_sell()

    # 未確定オーダー
    #api.get_incomplete_orders()
    #api.get_incomplete_orders_fx()

    #取引手数料
    #commissionrate = api.get_trading_commission()

    ## buy & sell BTC
    #amount = 0.005
    #api.buy(rate=buy, amount=amount)
    #print amount
    #api.sell(rate=sell, amount=amount)

    # スキャルピング
    #api.scalping(amount)

    # streaming ticker
    api.get_ticker_streaming()

    #time.sleep(3)
    #print sell_s, buy_s