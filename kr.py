# coding=utf-8
# author:xsl

import requests
import json
import re
import pymongo
import time
import os
import random
import datetime
from lxml import etree
from utils import ImageTool

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
        db_url = "mongodb://127.0.0.1:27017"
        self.db = pymongo.MongoClient(db_url)['sp_db'].tmp
        self.im_tool = ImageTool()
        db_url2 = 'mongodb://127.0.0.1:27017'
        db_url2 = 'mongodb://hwdb:Mg110120@122.112.235.92/instance_db'
        self.db2 = pymongo.MongoClient(db_url2)['instance_db']
    

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


    def html(self, url):
        proxy = self.get_proxy().get('proxy')
        print("proxy: {0}".format(proxy))
        response = self.session.get(url, headers=self.headers, proxies={"http": "http://{}".format(proxy)})
        if response.status_code == 200:
            data = response.text
            return data
        return "error"

    def paraseList(self, html):
        con = json.loads(html)
        data = con.get('data').get('items')

        arts = []
        for d in data:
            ID = d.get('post').get('id')
            title = d.get('post').get('title')
            user_id = d.get('post').get('user_id')
            user_name = d.get('post').get('user').get('name')
            url = "https://36kr.com/p/"+str(ID)
            arts.append({'title':title, 'a_id': str(ID), 'url': url, 'user_id': str(user_id), 'user_name': user_name})
        cursor = data[-1].get('id')
        self.db.insert_many(arts)
        print(cursor)
        return cursor


    def paraseList2(self, html):
        
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
        self.db.insert_many(arts)
        return cursor

    def next(self, cursor):
        url = "https://36kr.com/pp/api/motif/331/entities?per_page=20&b_id="+str(cursor)
        data = self.html(url)
        cursor = self.paraseList(data)
        if cursor == "error":
            return ""
        time.sleep(2)
        self.next(cursor)
        return "ok"

    def save(self, arts):
        self.db.insert_many(arts)

    
    def paraseOne(self, data):
        html = etree.HTML(data)

        jses = html.xpath('//script/text()')
        myjs = ''
        for js in jses:
            if 'window.initialState' in js:
                myjs = js
                break
        myjs = myjs.replace('window.initialState=', '')
        
        art = json.loads(myjs)
        art_detail = art.get('articleDetail')
        art_d = art_detail.get('articleDetailData')
        art_d = art_d.get('data')
            
        content = art_d.get('content')

        user = art_d.get('user')
        author = user.get('name')
        author_idf = user.get('id')
        pub_at = art_d.get('published_at')
        pub_at = datetime.datetime.strptime(pub_at, '%Y-%m-%d %H:%M:%S')


        con = etree.HTML(content)
        images = con.xpath('//img/@src')
        ims = self._uploadImages(images)

        trans_cont = content
        i = 0
        for im_url in images:
            new_url = ims[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_cont = content.replace(re_url,my_url)
            i += 1

        title = art_d.get('title')
        original_id = art_d.get('id')
        url = 'https://36kr.com/p/'+str(original_id)
        
        
        sa = {
            "title": title,
            "content": content,
            "transcoding": trans_cont,
            "original_url": url,
            "original_id": original_id,
            "author": author ,
            "author_idf": author_idf,
            "published_at": pub_at,
            "created_at": datetime.datetime.utcnow(),
            "type": '36kr',
            "images": ims
        }

        ins_id = self._save_one(sa)
        print('insert ok %s' % ins_id)
        return {'id':str(ins_id)}


    def _save_one(self, data):
        article = self.db2.article
        insid = article.insert_one(data).inserted_id
        return {'id':str(insid)}

    def _uploadImages(self, images):
        ims = []
        for im_url in images:
            im, typ = self._downloadImg(im_url)
            new_url = self.im_tool.upload(im, typ)
            ims.append(new_url)
            wait = random.random()
            print('download ok %s' % new_url)
            time.sleep(wait)
        return ims

    def _downloadImg(self, url):
        proxy = self.get_proxy().get('proxy')
        resp = self.session.get(url, headers=self.headers, proxies={"http": "http://{}".format(proxy)})
        content = resp.content
        mime_type = resp.headers['Content-Type']
        return (content, mime_type)

    def _fixText(self, text):
        new_t = ''.join(text)
        return new_t.strip()

    def spider_formdb(self):
        data = self.db.find()
        article = self.db2.article
        for d in data:
            if d.get('exsit') and d.get('exsit') == '1':
                print('exsit: {0}'.format(url))
                continue
            url = d.get('url')
            f = article.find_one({'original_url': url})
            if f:
                self.db.update_one({'url': url}, {"$set":{"exsit": '1'}})
                print('exsit: {0}'.format(url))
                continue
            print('start: {0}'.format(url))
            html = self.html(url)
            self.paraseOne(html)
            print('success: {0}'.format(url))
            time.sleep(1.5)


def test():
    sp = KrSpider()
    with open('/Users/xiusl/Desktop/a.html', 'r') as f:
        d = f.read()
        d = sp.paraseList(d)
        d = sp.insert_many(d)
        print(d)

def getList():
    sp = KrSpider()
    url = "https://36kr.com/pp/api/motif/331/entities?per_page=20"
    data = sp.html(url)
    cursor = sp.paraseList(data)
    sp.next(cursor)

def spiderOne():
    sp = KrSpider()
    sp.spider_formdb()

if __name__ == '__main__':
    spiderOne()
