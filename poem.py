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

        self.count = 50
        
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
        self.count = d.get('sumCount') or 50
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
        for i in range(1, self.count / 10):
            url = b_url+str(i)
            data = self.getHtmlByUrl(url)
            self.parase(data)
            wait = random.random()
            time.sleep(1+wait)

    def ss2(self, uid):
        #uid = '6888D54DC01ADF87C8193C8ED94E9BFE'
        b_url = 'https://app.gushiwen.cn/api/author/authorsw11.aspx?token=gswapi&id='+uid+'&page='
        for i in range(1, self.count / 10):
            url = b_url+str(i)
            print(url)
            data = self.getHtmlByUrl(url)
            self.parase2(data)
            wait = random.random()
            time.sleep(wait)

    def ss3(self):
        aut = self.db.author_a
        ds = aut.find()
        ids = []
        oids = ['6888D54DC01ADF87C8193C8ED94E9BFE', 'ACED84F2F3C2DEE0868E66E2F9DB18F4', '6911E98663CC56F9099A93D520AA2373', '19D5441382902DEA28FCFC1BB339B6FC', '37E32BAC4B670CF3DD527F1283C55042', '2B0F6E397BC8C61FE7A5DDBEFFC4A9C1', 'D97000E67A4E671D1D6EA5139B213765', '463BCE18212081C858CD02E3A8A51ED7', '29DCCC0D633A647C3707C8FBACB98BC3', '62BDA354811022A967718F87D53E8A57', '7D96E28ADE5BB3C02EE18A8DE47BA04F', '8D23D4EFC54F72C2385F0DF98A17F5A2', '5A157AEC67B3D27369B9F3E972CBCD1B']
        for d in ds:
            idd = d.get('idnew')
            if idd in oids:
                continue
            print(ids)
            self.ss2(idd)
            ids.append(idd)
            wait = random.random()
            time.sleep(wait)



# https://so.gushiwen.org/authors/

sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/b.htm')
#sp.paraseAuthor(data)
sp.ss3()

