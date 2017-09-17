"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

from lib.krakenapi import krakenfAPI
from lib.coincheckapi import CoincheckAPI
from lib.zaifapi import ZaifAPI
from lib.bitflyerapi import BitflyerAPI
import yaml

def main():
    """
    docstring
    """
    with open('config.yml', 'r') as yml:
        config = yaml.load(yml)

    amount = config["amount"]
    print "amount : " + str(amount)

    # coincheck
    cc_api = CoincheckAPI()
    cc_ask, cc_bid = cc_api.get_ticker()

    # zaif
    z_api = ZaifAPI()
    z_ask, z_bid = z_api.get_ticker()

    # kraken
    k_api = krakenfAPI()
    k_ask, k_bid = k_api.get_ticker()

    # bitflyer
    b_api = BitflyerAPI()
    b_ask, b_bid = b_api.get_ticker()

    ## coincheck x zaif
    resp = comparison("coincheck", cc_ask, cc_bid, "zaif", z_ask, z_bid)
    print resp
    if resp == 1:
        print "sell : coincheck"
        print "buy : zaif"
        #cc_api.bid(rate=cc_bid, amount=amount)
        #z_api.ask(rate=z_ask, amount=amount)
    elif resp == 2:
        print "sell : zaif"
        print "buy : coincheck"
        #z_api.bid(rate=z_bid, amount=amount)
        #cc_api.ask(rate=cc_ask, amount=amount)
    else:
        pass

    ## coincheck x kraken
    resp = comparison("coincheck", cc_ask, cc_bid, "kraken", k_ask, k_bid)
    print resp
    if resp == 1:
        print "sell : coincheck"
        print "buy : kraken"
        #cc_api.bid(rate=cc_bid, amount=amount)
        #k_api.ask(rate=k_ask, amount=amount)
    elif resp == 2:
        print "sell : zaif"
        print "buy : coincheck"
        #k_api.bid(rate=k_bid, amount=amount)
        #cc_api.ask(rate=cc_ask, amount=amount)
    else:
        pass

    ## bitflyer x coincheck
    resp = comparison("coincheck", cc_ask, cc_bid, "bitflyer", b_ask, b_bid)
    print resp
    if resp == 1:
        print "sell : coincheck"
        print "buy : kraken"
        #cc_api.bid(rate=cc_bid, amount=amount)
        #b_api.ask(rate=b_ask, amount=amount)
    elif resp == 2:
        print "sell : zaif"
        print "buy : coincheck"
        #b_api.bid(rate=b_bid, amount=amount)
        #cc_api.ask(rate=cc_ask, amount=amount)
    else:
        pass

    ## kraken x zaif
    #comparison("kraken", k_ask, k_bid, "zaif", z_ask, z_bid)
    ## bitflyer x zaif
    #comparison("bitflyer", b_ask, b_bid, "zaif", z_ask, z_bid)
    ## bitflyer x kraken
    #comparison("bitflyer", b_ask, b_bid, "kraken", k_ask, k_bid)

def comparison(a_name, a_ask, a_bid, b_name, b_ask, b_bid):
    """
    docstring
    """
    print "======================="

    if a_bid > b_ask:
        print a_name + "(bid) > " + b_name + "(ask)"
        print "difference :" + str(a_bid - b_ask)
        print "saya!!!"
        print "sell : " + a_name
        print "buy  : " + b_name

        ## next trade
        return 1

    if b_bid > a_ask:
        print b_name + "(bid) > " + a_name + "(ask)"
        print "difference :" + str(b_bid - a_ask)
        print "saya!!!"
        print "sell : " + b_name
        print "buy  : " + a_name
        ## next trade
        return 2

    return -1


if __name__ == "__main__":
    #getCoincCheckRate()
    #getZaifRate()
    main()
