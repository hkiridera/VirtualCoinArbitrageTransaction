# coding:utf-8
#!/usr/bin/env python
"""共通関数"""

import json
import traceback
import time
import requests
import yaml

with open('config.yml', 'r') as yml:
    config = yaml.load(yml)
f = open('data.csv', 'a')

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

def get(url, headers=None, params=None,data=None):
    try:
        response = requests.get(url, headers=headers, params=params, data=data)
        if response.status_code == 401:
            #print "try again!!"
            print response.url
            print response.text
            raise Exception('return status code is {}'.format(response.status_code))
        elif response.status_code != 200:
            print response.url
            print response.text
            raise Exception('return status code is {}'.format(response.status_code))

    except:
        traceback.print_exc()

    return response

def post(url, headers=None, data=None):
    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 401:
            #print "try again!!"
            print response.url
            print response.text
            raise Exception('return status code is {}'.format(response.status_code))
        elif response.status_code != 200:
            print response.url
            print response.text
            raise Exception('return status code is {}'.format(response.status_code))

    except:
        traceback.print_exc()

    return response


def delete(url, headers=None, data=None):
    try:
        response = requests.delete(url, headers=headers, data=data)
        
        if response.status_code == 401:
            #print "try again!!"
            raise Exception('return status code is {}'.format(response.status_code))
        elif response.status_code != 200:
            print response.url
            print response.text
            raise Exception('return status code is {}'.format(response.status_code))

    except:
        traceback.print_exc()

    return response

def post_slack(name=None,text=None):
    '''
    slackにメッセージを投稿する
    '''

    if name is None or text is None:
        return False

    try:
        requests.post(config["slack_address"], data = json.dumps({
            'text': text, # 投稿するテキスト
            'username': name, # 投稿のユーザー名
            'icon_emoji': ':saya:', # 投稿のプロフィール画像に入れる絵文字
            'link_names': 1, # メンションを有効にする
        }))
    except:
        traceback.print_exc()

    return True