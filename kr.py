# coding=utf-8
# author:xsl

import requests
import json
import re
import pymongo

class KrSpider(object):

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
        self.urls = []

    def html(self, url):
        response = self.session.get(url, headers=self.headers)
        date = response.text
        return data

    def paraseList(self, html):
        
        con = re.findall(r'window.initialState=(.*?)<', html)
        if len(con) < 1:
            return "error"
        con = con[0]
        con = json.loads(con)
        data = con.get('motifDetailData').get('data')
        data = data.get('motifArticleList').get('data')

        arts = []
        for d in data:
            title = d.get('post').get('title')
            ID = d.get('post').get('id')
            url = "https://36kr.com/p/"+str(ID)
            arts.append({'title':title, 'id': str(ID), 'url': url})
            
        cursor = data[-1].get('id')
        print(cursor)
        
        return arts



sp = KrSpider()
with open('/Users/xiusl/Desktop/a.html', 'r') as f:
    d = f.read()
    d = sp.paraseList(d)
    print(d)

