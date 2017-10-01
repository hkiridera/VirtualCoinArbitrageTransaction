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
    myutils.post_slack(name="さやちゃん", text="止まっちゃったよ")


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
    cc_api.initialize_ask()
    #zaif初期btc購入
    z_api.initialize_ask()  
    #bitflyer初期btc購入
    b_api.initialize_ask()

def main():
    """
    docstring
    """
    print "======================="

    amount = config["amount"]
    difference = config["difference"]

    ## 板価格を取得
    # coincheck
    cc_ask, cc_bid = cc_api.get_ticker()
    # zaif
    z_ask, z_bid = z_api.get_ticker()
    # kraken
    k_ask, k_bid = k_api.get_ticker()
    # bitflyer
    b_ask, b_bid = b_api.get_ticker()


    ## coincheck x zaif
    resp = comparison("coincheck", cc_ask, cc_bid, "zaif", z_ask, z_bid)
    if resp == 1:
        f.write("coincheck,sell," + str(cc_bid) +"\n")
        f.write("zaif,buy," + str(-z_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="coincheck", bid_amount=amount, ask_name="zaif", ask_price=z_ask * config["amount"]):
            cc_api.bid(rate=int(cc_bid), amount=amount)
            ## zaifだけbid,askが逆転
            #z_api.ask(rate=z_ask, amount=amount)
            z_api.bid(rate=int(z_bid), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("zaif,sell," + str(z_bid) +"\n")
        f.write("coincheck,buy," + str(-cc_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="zaif", bid_amount=amount, ask_name="coincheck", ask_price=cc_ask * config["amount"]):
            ## zaifだけbid,askが逆転
            #z_api.bid(rate=z_bid, amount=amount)
            z_api.ask(rate=int(z_ask), amount=amount)
            cc_api.ask(rate=int(cc_ask), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass
    
    ## bitflyer x coincheck
    resp = comparison("bitflyer", b_ask, b_bid, "coincheck", cc_ask, cc_bid)
    if resp == 1:
        f.write("bitflyer,sell," + str(b_bid) +"\n")
        f.write("coincheck,buy," + str(-cc_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="bitflyer", bid_amount=amount, ask_name="coincheck", ask_price=cc_ask * config["amount"]):
            b_api.bid(rate=int(b_bid), amount=amount)
            cc_api.ask(rate=cc_ask, amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("coincheck,sell," + str(cc_bid) +"\n")
        f.write("bitflyer,buy," + str(-b_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="coincheck", bid_amount=amount, ask_name="bitflyer", ask_price=b_ask * config["amount"]):
            cc_api.bid(rate=cc_bid, amount=amount)
            b_api.ask(rate=int(b_ask), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass

    ## bitflyer x zaif
    resp = comparison("bitflyer", b_ask, b_bid, "zaif", cc_ask, z_bid)
    if resp == 1:
        f.write("bitflyer,sell," + str(b_bid) +"\n")
        f.write("zaif,buy," + str(-z_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="bitflyer", bid_amount=amount, ask_name="zaif", ask_price=z_bid * config["amount"]):
            b_api.bid(rate=int(b_bid), amount=amount)
            ## zaifだけbid ask逆
            #z_api.ask(rate=z_ask, amount=amount)
            z_api.bid(rate=z_bid, amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"
        
    elif resp == 2:
        f.write("zaif,sell," + str(z_bid) +"\n")
        f.write("bitflyer,buy," + str(-cc_ask) +"\n")

        ## 売買可能な残高があるか
        if check_tradable(bid_name="zaif", bid_amount=amount, ask_name="bitflyer", ask_price=b_ask * config["amount"]):
            ## zaifだけbid ask逆
            z_api.ask(rate=z_ask, amount=amount)
            #z_api.bid(rate=z_bid, amount=amount)
            b_api.ask(rate=int(b_ask), amount=amount)
            print "buybuybuy!!!"
        else:
            print "Missing money"

    else:
        pass


    print "======================="

def comparison(a_name, a_ask, a_bid, b_name, b_ask, b_bid):
    """
    サヤ取りできるかを確認
    取引所間の差額を算出し、差額が設定値以上だったら1か2を返す
    設定値以下なら-1を返す
    """

    ## サヤ取りがa > bの場合
    if a_bid > b_ask:
        _difference = a_bid - b_ask
        print a_name + "(bid) > " + b_name + "(ask)"
        print "difference :" + str(_difference)
        print "config.difference : " + str(config["difference"])
        print "bid : " + a_name
        print "ask  : " + b_name
        if _difference > config["difference"]:
            print "saya1!!!"
            return 1

    ## サヤ取りがb > aの場合
    if b_bid > a_ask:
        _difference = b_bid - a_ask
        print b_name + "(bid) > " + a_name + "(ask)"
        print "difference :" + str(_difference)
        print "config.difference : " + str(config["difference"])
        print "bid : " + b_name
        print "ask  : " + a_name
        if _difference > config["difference"]:
            print "saya2!!!"
            return 2

    return -1


def check_tradable(bid_name, bid_amount, ask_name, ask_price):
    ## 売買可能フラグ
    bidflg = False
    askflg = False

    ## btcを持っているかチェック
    if bid_name == "bitflyer":
        if b_api.check_bid(amount=bid_amount):
            bidflg = True

    if bid_name == "coincheck":
        if cc_api.check_bid(amount=bid_amount):
            bidflg = True

    if bid_name == "kraken":
        if k_api.check_bid(amount=bid_amount):
            bidflg = True

    if bid_name == "zaif":
        if z_api.check_bid(amount=bid_amount):
            bidflg = True


    ## jpyを持っているかチェック
    if ask_name == "bitflyer":
        if b_api.check_ask(amount=ask_price):
            askflg = True

    if ask_name == "coincheck":
        if cc_api.check_ask(amount=ask_price):
            askflg = True

    if ask_name == "kraken":
        if k_api.check_ask(amount=ask_price):
            askflg = True

    if ask_name == "zaif":
        if z_api.check_ask(amount=ask_price):
            askflg = True

    print "bidflg : " + str(bidflg)
    print "askflg : " + str(askflg)

    ## 結果を返す
    if bidflg == True and askflg == True:
        return True
    else:
        return False


if __name__ == "__main__":
    #getCoincCheckRate()
    #getZaifRate()
    # 停止時の処理
    atexit.register(_sttop_process)

    # 初期化
    #initialize()

    while(True):
        main()
        sleep(config["interval"])
