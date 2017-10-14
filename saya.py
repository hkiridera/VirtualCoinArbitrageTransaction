# coding:utf-8
#!/usr/bin/env python
"""This is a test program."""

import atexit
import signal
import sys
import yaml

from lib.bitflyerapi import BitflyerAPI
from lib.coincheckapi import CoincheckAPI
from lib.krakenapi import krakenfAPI
from lib.zaifapi import ZaifAPI
import lib.myutils as myutils

from time import sleep

with open('config.yml', 'r') as yml:
    config = yaml.load(yml)
f = open('data.csv', 'a')

cc_api = CoincheckAPI()
z_api = ZaifAPI()
k_api = krakenfAPI()
b_api = BitflyerAPI()

def _sttop_process():
    '''
    終了時に実行
    '''
    myutils.post_slack(name="さやちゃん", text="止まっちゃったよ…")


def handler(signal, frame):
    """
    強制終了用ハンドラ
    ctl + cで止まる
    """
    print('Oh, i will be die ...')
    sys.exit(0)
    f.close()
signal.signal(signal.SIGINT, handler)

def initialize():
    #coincheckで初期btc購入
    cc_api.initialize_buy()
    #zaif初期btc購入
    z_api.initialize_buy()  
    #bitflyer初期btc購入
    b_api.initialize_buy()

def main():
    """
    docstring
    """
    print "======================="

    amount = config["amount"]
    difference = config["difference"]

    ## 板価格を取得
    # coincheck
    cc_buy, cc_sell = cc_api.get_ticker()
    # zaif
    z_buy, z_sell = z_api.get_ticker()
    # kraken
    k_buy, k_sell = k_api.get_ticker()
    # bitflyer
    b_buy, b_sell = b_api.get_ticker()


    ## coincheck x zaif
    resp = comparison("coincheck", cc_buy, cc_sell, "zaif", z_buy, z_sell)
    if resp == 1:
        f.write("coincheck,sell," + str(cc_sell) +"\n")
        f.write("zaif,buy," + str(-z_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="coincheck", sell_amount=amount, buy_name="zaif", buy_price=z_buy * config["amount"]):
            cc_api.sell(rate=int(cc_sell), amount=amount)
            ## zaifだけsell,buyが逆転
            #z_api.buy(rate=z_buy, amount=amount)
            z_api.sell(rate=int(z_sell), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("zaif,sell," + str(z_sell) +"\n")
        f.write("coincheck,buy," + str(-cc_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="zaif", sell_amount=amount, buy_name="coincheck", buy_price=cc_buy * config["amount"]):
            ## zaifだけsell,buyが逆転
            #z_api.sell(rate=z_sell, amount=amount)
            z_api.buy(rate=int(z_buy), amount=amount)
            cc_api.buy(rate=int(cc_buy), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass
    
    ## bitflyer x coincheck
    resp = comparison("bitflyer", b_buy, b_sell, "coincheck", cc_buy, cc_sell)
    if resp == 1:
        f.write("bitflyer,sell," + str(b_sell) +"\n")
        f.write("coincheck,buy," + str(-cc_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="bitflyer", sell_amount=amount, buy_name="coincheck", buy_price=cc_buy * config["amount"]):
            b_api.sell(rate=int(b_sell), amount=amount)
            cc_api.buy(rate=cc_buy, amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("coincheck,sell," + str(cc_sell) +"\n")
        f.write("bitflyer,buy," + str(-b_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="coincheck", sell_amount=amount, buy_name="bitflyer", buy_price=b_buy * config["amount"]):
            cc_api.sell(rate=cc_sell, amount=amount)
            b_api.buy(rate=int(b_buy), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass

    ## bitflyer x zaif
    resp = comparison("bitflyer", b_buy, b_sell, "zaif", cc_buy, z_sell)
    if resp == 1:
        f.write("bitflyer,sell," + str(b_sell) +"\n")
        f.write("zaif,buy," + str(-z_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="bitflyer", sell_amount=amount, buy_name="zaif", buy_price=z_sell * config["amount"]):
            b_api.sell(rate=int(b_sell), amount=amount)
            ## zaifだけsell buy逆
            #z_api.buy(rate=z_buy, amount=amount)
            z_api.sell(rate=z_sell, amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("zaif,sell," + str(z_sell) +"\n")
        f.write("bitflyer,buy," + str(-cc_buy) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(sell_name="zaif", sell_amount=amount, buy_name="bitflyer", buy_price=b_buy * config["amount"]):
            ## zaifだけsell buy逆
            z_api.buy(rate=z_buy, amount=amount)
            #z_api.sell(rate=z_sell, amount=amount)
            b_api.buy(rate=int(b_buy), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass


    print "======================="

def comparison(a_name, a_buy, a_sell, b_name, b_buy, b_sell):
    """
    サヤ取りできるかを確認
    取引所間の差額を算出し、差額が設定値以上だったら1か2を返す
    設定値以下なら-1を返す
    """

    ## サヤ取りがa > bの場合
    if a_sell > b_buy:
        _difference = a_sell - b_buy
        print a_name + "(sell) > " + b_name + "(buy)"
        print "difference :" + str(_difference)
        print "config.difference : " + str(config["difference"])
        print "sell : " + a_name
        print "buy  : " + b_name
        if _difference > config["difference"]:
            print "saya1!!!"
            return 1

    ## サヤ取りがb > aの場合
    if b_sell > a_buy:
        _difference = b_sell - a_buy
        print b_name + "(sell) > " + a_name + "(buy)"
        print "difference :" + str(_difference)
        print "config.difference : " + str(config["difference"])
        print "sell : " + b_name
        print "buy  : " + a_name
        if _difference > config["difference"]:
            print "saya2!!!"
            return 2

    return -1


def check_tradable(sell_name, sell_amount, buy_name, buy_price):
    ## 売買可能フラグ
    sellflg = False
    buyflg = False

    ## btcを持っているかチェック
    if sell_name == "bitflyer":
        if b_api.check_sell(amount=sell_amount):
            sellflg = True

    if sell_name == "coincheck":
        if cc_api.check_sell(amount=sell_amount):
            sellflg = True

    if sell_name == "kraken":
        if k_api.check_sell(amount=sell_amount):
            sellflg = True

    if sell_name == "zaif":
        if z_api.check_sell(amount=sell_amount):
            sellflg = True


    ## jpyを持っているかチェック
    if buy_name == "bitflyer":
        if b_api.check_buy(amount=buy_price):
            buyflg = True

    if buy_name == "coincheck":
        if cc_api.check_buy(amount=buy_price):
            buyflg = True

    if buy_name == "kraken":
        if k_api.check_buy(amount=buy_price):
            buyflg = True

    if buy_name == "zaif":
        if z_api.check_buy(amount=buy_price):
            buyflg = True

    print "sellflg : " + str(sellflg)
    print "buyflg : " + str(buyflg)

    ## 結果を返す
    if sellflg == True and buyflg == True:
        return True
    else:
        return False


if __name__ == "__main__":

    ## 開始時のメッセージ
    myutils.post_slack(name="さやちゃん",text="さやちゃん始めるよー")

    #getCoincCheckRate()
    #getZaifRate()
    # 停止時の処理
    atexit.register(_sttop_process)

    # 初期化
    if config["initialize"]:
        initialize()

    while(True):
        main()
        sleep(config["interval"])
