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
from utils import ImageTool


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

        
    def _init_db(self):
        mongo_url = 'mongodb://127.0.0.1:27017'
        client = pymongo.MongoClient(mongo_url)
        db = client['poem_db']
        self.db = db

    def _fixText(self, text):
        new_t = ''.join(text)
        return new_t.strip()

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    def getHtmlByUrl(self, url):
        self.url = url
        proxy = self.get_proxy().get('proxy')
        proxies = {"http": "http://{}".format(proxy)}
        try:
            response = self.session.get(url, headers=self.headers, verify=False, proxies=proxies)
            data = response.content
            response.encoding = "utf-8"
        except:
            print(url)
            return "123"
        return data

    def getHtmlByFile(self, path):
        f = open(path, 'r')
        data = f.read()
        return data

    def _uploadImages(self, images):
        ims = []
        for im_url in images:
            im, typ = self.im_tool.download(im_url)
            new_url = self.im_tool.upload(im, typ)
            ims.append(new_url)
            wait = random.random()
            print('download ok %s' % new_url)
            time.sleep(wait)
        return ims

    def paraseAuthor(self, data):
        html = etree.HTML(data)
        
        sons = html.xpath('//div[@class="sonspic"]')
        for s in sons:
            name = s.xpath('./div/p/a/b/text()')
            name = self._fixText(name)

            url = s.xpath('./div/div[@class="divimg"]/a/@href')
            url = self._fixText(url)

            cover = s.xpath('./div/div[@class="divimg"]/a/img/@src')
            cover = self._fixText(cover)
            
            d = {'name':name, 'o_url': url, 'cover': cover} 
            self.save(d)

    def save(self, data):
        print(data)
        aut = self.db.author_a
        a = aut.find_one({'nameStr': data['nameStr']})
        if a:
            print('exsit')
        else:
            ins_id = aut.insert_one(data).inserted_id
            print(ins_id)

    def parase(self, data):
        data = data.decode('utf-8')
        d = json.loads(data)
        
        li = d.get('authors')
        for l in li:
            self.save(l)

    def parase2(self, data):
        data = data.decode('utf-8')
        d = json.loads(data)
        li = d.get('tb_gushiwens')
        for l in li:
            a = l
            for b in self.ex:
                if b in a.keys():
                    a.pop(b)
            self.save2(a)

    def save2(self, data):
        aut = self.db.poem_a
        a = aut.find_one({'idnew': data['idnew']})
        if a:
            print('exsit')
        else:
            ins_id = aut.insert_one(data).inserted_id
            print(ins_id)

    def ss(self):
        b_url = 'http://app.gushiwen.cn/api/author/Default10.aspx?token=gswapi&page='
        for i in range(1, 101):
            url = b_url+str(i)
            data = self.getHtmlByUrl(url)
            self.parase(data)
            wait = random.random()
            time.sleep(1+wait)

    def ss2(self):
        uid = '6888D54DC01ADF87C8193C8ED94E9BFE'
        b_url = 'https://app.gushiwen.cn/api/author/authorsw11.aspx?token=gswapi&id='+uid+'&page='
        for i in range(1, 101):
            url = b_url+str(i)
            print(url)
            data = self.getHtmlByUrl(url)
            self.parase2(data)
            wait = random.random()
            time.sleep(wait)

    def ss3(self):
        aut = self.db.author_a
        ds = aut.find()
        for d in ds:
            print(d)
            break


# https://so.gushiwen.org/authors/

sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/b.htm')
#sp.paraseAuthor(data)
sp.ss3()

