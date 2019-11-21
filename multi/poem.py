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
    #    self._init_oids()
        self.bad_url = []
        
    def _init_db(self):
        mongo_url = 'mongodb://127.0.0.1:27017'
        client = pymongo.MongoClient(mongo_url)
        db = client['poem_db']
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
        self.url = url
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


    def parase_fy(self, data, url):
        data = data.decode('utf-8')
        try:
            d = json.loads(data)
            a = d.get('tb_gushiwen')
            yizhu = a.get('yizhu')
            idd = a.get('idnew')
            type = a.get('type')

            b = d.get('tb_fanyis').get('fanyis')
            if len(b) > 0:
                fy = b[0]
                fyd = {'oid':idd,'author':fy.get('nameStr'),'name': fy.get('nameStr'), 'yuanchuang': fy.get('isYuanchuang'), 'cankao': fy.get('cankao'), 'cont': fy.get('cont')}
                self.save_fy(fyd)

            self.upGs(yizhu, idd, type)
        except:
            print('jsonload error')
            self.bad_url.append(url)


    def upGs(self, yizhu, idd , ty):
        aut = self.db.poem_a
        aut.update_one({'idnew': idd}, {'$set':{'type':ty, 'yizhu': yizhu}})
    
    def save_fy(self, data):
        fy_col = self.db.fy_a
        fy = fy_col.find_one({'oid': data['oid']})
        if fy:
            print('exsit')
        else:
            ins_id = fy_col.insert_one(data).inserted_id
            print(ins_id)

        

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
        for d in ds:
            idd = d.get('idnew')
            if idd in self.oids:
                continue
            print(ids)
            self.ss2(idd)
            ids.append(idd)
            wait = random.random()
            time.sleep(wait)

    def ss4(self):
        aut = self.db.poem_a
        ds = aut.find()
        b_url = 'https://app.gushiwen.cn/api/shiwen/shiwenv11.aspx?token=gswapi&id='
        for d in ds:
            idd = d.get('idnew')
            url = b_url+idd
            data = self.getHtmlByUrl(url)
            self.parase_fy(data, url)
            wait = random.random()
            print('wait: {}'.format(wait+1))
            print('self.bad_url')
            time.sleep(wait+1)
            

        with open('./a.py', 'w') as f:
            f.write(','.join(self.bad_url))


# https://so.gushiwen.org/authors/

sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/b.htm')
#sp.paraseAuthor(data)
sp.ss3()

