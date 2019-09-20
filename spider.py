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
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
        self._init_db()
        self.im_tool = ImageTool()

        
    def _init_db(self):
        mongo_url = os.getenv('MONGO_URL') or 'mongodb://127.0.0.1:27017'
        print(mongo_url)
        client = pymongo.MongoClient(mongo_url)
        db = client['instance_db']
        self.db = db

    def _fixText(self, text):
        new_t = ''.join(text)
        return new_t.strip()

    def getHtmlByUrl(self, url):
        self.url = url
        response = self.session.get(url, headers=self.headers)
        data = response.text
        return data

    def getHtmlByFile(self, path):
        f = open(path, 'r')
        data = f.read()
        return data

    def paraseData36kr(self, data):
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

        ins_id = self._save(sa)
        print('insert ok %s' % ins_id)
        return {'id':str(ins_id)}

    def _save(self, data):
        article = self.db.article
        insid = article.insert_one(data).inserted_id
        return {'id':str(insid)}

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

    def paraseDataLaohu(self, data):
        html = etree.HTML(data)
        
        title = html.xpath('//h1[@class="article-title"]/text()')
        title = self._fixText(title)

        author = html.xpath('//span[@class="article-author"]/text()')
        author = self._fixText(author)

        pub = html.xpath('//span[@class="article-date"]/text()')
        pub = self._fixText(pub)
        pub = pub[2:]
        pub = datetime.datetime.strptime(pub, '%Y-%m-%d %H:%M')

        content = html.xpath('//div[@class="article-content"]')
        content = etree.tostring(content[0], encoding="utf8", pretty_print=True, method="html")
        content = content.decode('utf8')

        images = html.xpath('//div[@class="article-content"]')[0].xpath('.//img/@src')
        ims = self._uploadImages(images)

        trans_cont = content
        i = 0
        for im_url in images:
            new_url = ims[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_cont = content.replace(re_url,my_url)
            i += 1

        sa = {
            "title": title,
            "content": content,
            "transcoding": trans_cont,
            "original_url": self.url,
            "original_id": "",
            "author": author ,
            "author_idf": "",
            "published_at": pub,
            "created_at": datetime.datetime.utcnow(),
            "type": 'laohu',
            "images": ims
        }

        ins_id = self._save(sa)
        print(sa)
        print('insert ok %s' % ins_id)
        return {'id':str(ins_id)}





#sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/laohu.htm')
#sp.paraseDataLaohu(data)

