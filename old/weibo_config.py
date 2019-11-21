#!/usr/bin/env python
# coding=utf-8
# author: xsl

class Config():


    pre_login_params = {
        "entry": "weibo",
        "callback": "sinaSSOController.preloginCallBack",
        "su": "",
        "rsakt": "mod",
        "checkpin": 1,
        "client": "ssologin.js(v1.4.19)",
        "_": "1521133114145"
    }

    login_params = {
        "entry": "weibo",
        "getway": 1,
        "form": "",
        "savestate": 7,
        'userticket': '1',
        'ssosimplelogin': '1',
        'pwencode': 'rsa2',
        "vsnf": 1,
        'vsnval': '',
        "su": "",
        "sp": "",
        "service": "miniblog",
        "servertime": "",
        "nonce": "",
        "rsakv": "",
        "encoding": "UTF-8",
        "url":"https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
        "returntype": "META"
    }

    search_params = {
        'type': 'all',
        'queryVal': '',
        'containerid': '100103type=3&q='
    }

    def __init__(self):
        pass
