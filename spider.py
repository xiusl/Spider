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
from utils import ImageTool, DateEncoder


class Spider():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
        self.im_tool = ImageTool()


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
            "original_id": str(original_id),
            "author": author ,
            "author_idf": str(author_idf),
            "published_at": pub_at,
            "created_at": datetime.datetime.utcnow(),
            "type": '36kr',
            "images": ims
        }

        self._save(sa)
        return {'id':'123'}

    def paraseJianShu(self, data):
        html = etree.HTML(data)
        a = html.xpath('//script[@type="application/json"]/text()')
        a = self._fixText(a)

        b = json.loads(a)
        note = b.get('props').get('initialState').get('note').get('data')
        free_content = note.get('free_content')
        # print(free_content)

        u = note.get('user')

        title = note.get('public_title')
        author = u.get('nickname')
        author_id = str(u.get('id'))
        ori_id = str(note.get('id'))
        pub = note.get('first_shared_at')
        pub = datetime.datetime.utcfromtimestamp(int(pub))
    
        trans_cont = free_content
        
        e_cont = etree.HTML(trans_cont)
        images = e_cont.xpath('//img/@data-original-src')
        images = ['http:'+im for im in images]
        ims = self._uploadImages(images)

        for i, im_url in enumerate(images):
            new_url = ims[i]
            re_url = "data-original-src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_cont = trans_cont.replace(re_url,my_url)

        # print(trans_cont)

        sa = {
            "title": title,
            "content": free_content,
            "transcoding": trans_cont,
            "original_url": self.url,
            "original_id": ori_id,
            "author": author ,
            "author_idf": author_id,
            "published_at": pub,
            "created_at": datetime.datetime.utcnow(),
            "type": 'jianshu',
            "images": ims
        }
        self._save(sa)
        return {'id':'123'}

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

        self._save(sa)
        return {'id':"123"}


    def _save(self, data):
        url = 'https://ins-api.sleen.top/spider/article'
        #url = 'http://127.0.0.1:5000/spider/article'
        d = {'article': json.dumps(data, cls=DateEncoder)}
        da = json.dumps(d)
        res = self.session.post(url, headers={'Content-Type':'application/json'}, data=da)
        print('{0}: {1}'.format(data['title'], res.status_code))
        return {'id': '123'}

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





#sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/jian.html')
#sp.paraseDataLaohu(data)
#data = sp.getHtmlByUrl('https://www.jianshu.com/p/ce744d3f6af5')
#sp.paraseJianShu(data)

