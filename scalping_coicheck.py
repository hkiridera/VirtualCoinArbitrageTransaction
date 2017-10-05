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
    myutils.post_slack(name="さやちゃん", text="coincheckのスキャルピング止まっちゃったよ…")


def handler(signal, frame):
    """
    強制終了用ハンドラ
    ctl + cで止まる
    """
    print('Oh, i will be die ...')
    sys.exit(0)
    f.close()
signal.signal(signal.SIGINT, handler)

def cc_scalping():
    amount = config["coincheck"]["amount"]
    cc_api.scalping(amount)

if __name__ == "__main__":

    ## 開始時のメッセージ
    myutils.post_slack(name="さやちゃん",text="coincheckのスキャルピング始めるよー")

    # 停止時の処理
    atexit.register(_sttop_process)

    while(True):
        cc_scalping()
        #sleep(config["interval"])