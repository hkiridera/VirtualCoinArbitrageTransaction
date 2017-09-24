# coding:utf-8
#!/usr/bin/env python
"""共通関数"""

import traceback
import time
import requests

def nonce():
    """
    docstring
    """
    _nonce = int(time.time() * 1000000000)
    #print "nonce : " + str(_nonce)
    return _nonce

def nonce2():
    """
    docstring
    """
    _nonce = float(time.time())
    #print "nonce : " + str(_nonce)
    return _nonce

def get(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
    except:
        traceback.print_exc()

    if response.status_code == 401:
        #print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response

def post(url, headers=None, data=None):
    try:
        response = requests.post(url, headers=headers, data=data)
    except:
        traceback.print_exc()

    if response.status_code == 401:
        #print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response


def delete(url, headers=None, data=None):
    try:
        response = requests.delete(url, headers=headers, data=data)
    except:
        traceback.print_exc()
        
    if response.status_code == 401:
        #print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response