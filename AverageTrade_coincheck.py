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
import multiprocessing

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
    myutils.post_slack(name="さやちゃん", text="平均トレード止まっちゃったよ…")


def handler(signal, frame):
    """
    強制終了用ハンドラ
    ctl + cで止まる
    """
    print('Oh, i will be die ...')
    sys.exit(0)
    f.close()
signal.signal(signal.SIGINT, handler)

def average():
    ## 板価格を取得
    # coincheck
    cc_buy, cc_sell = cc_api.get_ticker()
    # zaif
    z_buy, z_sell = z_api.get_ticker()
    # kraken
    #k_buy, k_sell = k_api.get_ticker()
    # bitflyer
    b_buy, b_sell = b_api.get_ticker()

    av_buy = (cc_buy + z_buy + b_buy)/3
    av_sell = (cc_sell + z_sell + b_sell)/3

    print av_buy, av_sell
    return av_buy, av_sell, cc_buy, cc_sell

def main():
    ## 
    print ("==================")
    ## 板価格を取得
    # coincheck
    av_buy, av_sell, cc_buy, cc_sell = average()
    if (av_buy)> cc_buy:
        cc_api.IFD(config["coincheck"]["amount"], buy=cc_buy, sell=av_sell)

if __name__ == "__main__":

    ## 開始時のメッセージ
    myutils.post_slack(name="さやちゃん",text="平均トレード始めるよー")

    # 停止時の処理
    atexit.register(_sttop_process)

    while(True):
        main()
        sleep(config["interval"])
