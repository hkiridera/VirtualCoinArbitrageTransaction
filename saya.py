"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

from lib.krakenapi import krakenfAPI
from lib.coincheckapi import CoincheckAPI
from lib.zaifapi import ZaifAPI

def getCoincCheckRate():
    api = CoincheckAPI()
    ask,bid = api.getTicker()
    return ask,bid 

def getZaifRate():
    api = ZaifAPI()
    ask,bid = api.getTicker()
    return ask,bid 

def getKrakenRate():
    api = krakenfAPI()
    ask,bid = api.getTicker()
    return ask,bid 

def main():
    # coincheck
    cc_api = CoincheckAPI()
    cc_ask,cc_bid = cc_api.getTicker()

    # zaif
    z_api = ZaifAPI()
    z_ask,z_bid = z_api.getTicker()

    # kraken
    k_api = krakenfAPI()
    k_ask,k_bid = k_api.getTicker()

    ## coincheck x zaif
    comparison("coincheck", cc_ask, cc_bid, "zaif", z_ask, z_bid)
    ## coincheck x kraken
    comparison("coincheck", cc_ask, cc_bid, "kraken", k_ask, k_bid)
    ## kraken x zaif
    comparison("kraken", k_ask, k_bid, "zaif", z_ask, z_bid)


def comparison(aName, aAsk, aBid, bName, bAsk, bBid):
    print ("=======================")

    if(aBid > bAsk):
        print aName + "(bid) > " + bName + "(ask)"
        print "difference :" + str(aBid - bAsk)
        print "saya!!!"
        print "sell : " + aName
        print "buy  : " + bName
        
        ## next trade
    #else: 
        #print "coincheck(ask) > zaif(bid)"
        #print "difference :" + str(cc_ask - z_bid)

    if(bBid > aAsk):
        print bName + "(bid) > " + aName + "(ask)"
        print "difference :" + str(bBid - aAsk)
        print "saya!!!"
        print "sell : " + bName
        print "buy  : " + aName
        ## next trade
    #else: 
        #print "zaif(ask) > coincheck(bid)"
        #print "difference :" + str(z_ask - cc_bid)



if __name__ == "__main__":
    #getCoincCheckRate()
    #getZaifRate()
    main()
