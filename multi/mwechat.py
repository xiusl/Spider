# coding=utf-8
# author:xsl

import requests
import json
import pymongo
import datetime
import time
import random
import os
from lxml import etree
from urllib.parse import parse_qs, urlparse, urlencode

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Spider():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Content-Type': 'charset=utf8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
        self._init_db()
        #self.im_tool = ImageTool()
        self.ex = ['axing', 'bxing', 'cxing', 'dxing', 'exing', 'langsongAuthor', 'langsongAuthorPY', 
            'pinglunCount', 'beijingIspass', 'shangIspass', 'yizhuIspass', 'yizhuYuanchuang']

        self.count = 50
        self.base_url = 'https://mp.weixin.qq.com/mp/profile_ext?'
        
    def _init_db(self):
        mongo_url = 'mongodb://127.0.0.1:27017'
        client = pymongo.MongoClient(mongo_url)
        db = client['mwechat_db']
        self.db = db

    def agents(self):
        li = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
              "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
              "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
              "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
              "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
              "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
              "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
              "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",]
        return random.choice(li)


    def _init_oids(self):
        with open('./oids.txt') as f:
            a = f.read()
            a = a.replace(' ', '')
            d = a.split(',')
            e = [ x[1:-1] for x in d]
            self.oids = e


    def _fixText(self, text):
        new_t = ''.join(text)
        return new_t.strip()

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    def getHtmlByUrl(self, url):
        proxy = self.get_proxy().get('proxy')
        proxies = {"http": "http://{}".format(proxy)}
        self.headers['User-Agent'] = self.agents()
        try:
            response = self.session.get(url, headers=self.headers, verify=False, proxies=proxies)
            data = response.content
            response.encoding = "utf-8"
        except:
            self.bad_url.append(url)
            print(url)
            return "123"
        return data

    def getHtmlByFile(self, path):
        f = open(path, 'r')
        data = f.read()
        return data

    def save(self, data):
        print(data)
        aut = self.db.author_a
        a = aut.find_one({'nameStr': data['nameStr']})
        if a:
            print('exsit')
        else:
            ins_id = aut.insert_one(data).inserted_id
            print(ins_id)

    def params(self):
        biz = 'MzA3NTE5MzQzMA==' # 公众号 idf
        offset = 0  # 分页
        uin = 'Mjk5MDExNjQ4MQ=='  # 公众号 idf
        key = '02159478fef6853298301b295534e99699f4926cef30d1b26364b32d76e2ede4686e4154185cd2bea3e6c8d30ec6d656bb1601b535bf88f0ad1b9fdcc8ebc2b99d9f4096e740cf3f80e0172ef27ba1c6'
        ticket = 'Z5B5BNn0e+4z/BREiEYdOBBhpXku094mrW4bAL3EENWdlc/G+71lGDybhtLcpjKd'
        token = '1038_naLwPs4L0NSPsseL2R22FwyhoPBtkhFCrRXf4A~~'
        p = {
            'action': 'getmsg',
            '__biz': biz,
            'f': 'json',
            'offset': offset,
            'count': 10,
            'is_ok': 1,
            'scene': 124,
            'uin': uin,
            'key': key,
            'pass_ticket': ticket,
            'appmsg_token': token,
            'x5': 0,
            'wxtoken': '',
        }
        l = ''
        for k,v in p.items():
            l += "{}={}&".format(k, v)
        l = l[:-1]
        return l

    def cookie(self):
        txt = "devicetype=iPhoneiOS13.2.3; lang=zh_CN; pass_ticket=Z5B5BNn0e4z/BREiEYdOBBhpXku094mrW4bAL3EENWdlc/G71lGDybhtLcpjKd; version=17000831; wap_sid2=CIGd5pELElxvbkxfZTg0eGZaTnlMM2V4UnJoRkJLQklDUXZ4azBCNVA0cnEzUFU1SDB1dFRfdl9qeUlIWjVOZ3BmSmRSWVZJRndlYmQ2cjZ4TGF1SEJ1RmtRM2RydzRFQUFBfjCF+bfvBTgNQJVO; wxuin=2990116481; pgv_pvid=4685994470; tvfe_boss_uuid=e98ad03a00e6a3fe"
        return txt

    def fix(self):
        url = 'https://mp.weixin.qq.com/mp/profile_ext?'
        p = self.params()
        
        p = "action=getmsg&__biz=MzA3NTE5MzQzMA==&f=json&offset=10&count=10&is_ok=1&scene=124&uin=Mjk5MDExNjQ4MQ%3D%3D&key=02159478fef6853298301b295534e99699f4926cef30d1b26364b32d76e2ede4686e4154185cd2bea3e6c8d30ec6d656bb1601b535bf88f0ad1b9fdcc8ebc2b99d9f4096e740cf3f80e0172ef27ba1c6&pass_ticket=Z5B5BNn0e%2B4z%2FBREiEYdOBBhpXku094mrW4bAL3EENWdlc%2FG%2B71lGDybhtLcpjKd&wxtoken=&appmsg_token=1038_naLwPs4L0NSPsseL2R22FwyhoPBtkhFCrRXf4A~~&x5=0&f=json"
        url += p
        print(url)
        cookies = self.cookie()
        cookies2 = dict(map(lambda x:x.split('='), cookies.split(";")))
        print(cookies2)
        for k,v in cookies2.items():
            self.session.cookies[k]=v
        response = self.session.get(url, headers=self.headers, verify=False)
        data = response.content
        print(data)

# https://so.gushiwen.org/authors/

sp = Spider()
sp.fix()


