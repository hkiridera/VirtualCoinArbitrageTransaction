"""This is a test program."""

# coding:utf-8
#!/usr/bin/env python

import time
import requests

def nonce():
    """
    docstring
    """
    _nonce = int(time.time() * 1000000000)
    return _nonce

def get(url, headers=None, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:
        print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response

def post(url, headers=None, data=None):
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 401:
        print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response


def delete(url, headers=None, data=None):
    response = requests.delete(url, headers=headers, data=data)
    if response.status_code == 401:
        print "try again!!"
        raise Exception('return status code is {}'.format(response.status_code))
    elif response.status_code != 200:
        print response.url
        print response.text
        raise Exception('return status code is {}'.format(response.status_code))
    return response