# coding=utf-8
# author:xsl

import requests
import json
import re
import pymongo
import datetime
import time
import random
import os
import logging
import html as ex_html
from lxml import etree
from utils import ImageTool, DateEncoder, send_error
from parse import wx_parse


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
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(name)s %(levelname)s %(message)s",
                            datefmt="%Y-%m-%d  %H:%M:%S %a")
        self.debug = os.environ.get('DEBUG') or False


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

    def parseSsPi(self, data):
        #data = ex_html.unescape(data)
        cont = re.findall(r'window.__INITIAL_STATE__=(.*?);\(function\(\){var', data)
        cont = cont[0]
        cont = json.loads(cont)
        post = cont.get('post')
        art = post.get('articleInfo')

        title = art.get('title')
        author = art.get('author').get('nickname')
        author_idf = str(art.get('author').get('id'))

        pub_at = art.get('released_time')
        pub_at = datetime.datetime.utcfromtimestamp(int(pub_at)) 

    
        con = art.get('body')
        html = etree.HTML(con)
        images = html.xpath('//img/@src')
        ims = self._uploadImages(images)
        
        trans_cont = con
        for i, im_url in enumerate(images):
            n_url = ims[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+n_url+"\""
            trans_cont = trans_cont.replace(re_url,my_url)

        original_id = str(art.get('id'))
        url = 'https://sspai.com/post/'+original_id

        con = con.replace('<html><head></head><body>', '')
        con = con.replace('</body></html>', '')

        trans_cont = trans_cont.replace('<html><head></head><body>', '')
        trans_cont = trans_cont.replace('</body></html>', '')

        sa = {
            "title": title,
            "content": con,
            "transcoding": trans_cont,
            "original_url": url,
            "original_id": original_id,
            "author": author ,
            "author_idf": author_idf,
            "published_at": pub_at,
            "created_at": datetime.datetime.utcnow(),
            "type": 'sspi',
            "images": ims
        }

        self._save(sa)
        return {'id':'123'}



    def parseData36kr(self, data):
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

    def parseJianShu(self, data):
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

    def parseDataLaohu(self, data):
        html = etree.HTML(data)
        
        title = html.xpath('//h1[@class="article-title"]/text()')
        title = self._fixText(title)

        author = html.xpath('//span[@class="article-author"]/a/text()')
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

    def parseWechat(self, data):
        
        res = wx_parse(data)
        images = res['original_images']
        my_images = self._uploadImages(images)

        trans_content = res['content']
        i = 0
        for im_url2 in images:
            myimurl = my_images[i]
            re_url1 = "data-src=\"" + im_url2 + "\""
            re_url2 = "src=\"" + im_url2 + "\""
            my_re = "src=\"" + myimurl + "\""
            trans_content = trans_content.replace(re_url1, my_re)
            trans_content = trans_content.replace(re_url2, my_re)
            i += 1

        res['images'] = my_images
        res['transcoding'] = trans_content
        res['original_url'] = self.url
        self._save(res)
        return {'id': '123'}

    def _save(self, data):
        url = 'https://ins-api.sleen.top/spider/article'
        if self.debug:
            url = 'http://127.0.0.1:5000/spider/article'
        d = {'article': json.dumps(data, cls=DateEncoder)}
        da = json.dumps(d)
        res = self.session.post(url, headers={'Content-Type':'application/json'}, data=da)
        print('{0}: {1}'.format(data['title'], res.status_code))
        if res.status_code > 200:
            send_error(self.url, '解析成功，但是保存失败。请检查接受服务器连接{}，<br/>数据：{}'.format(url, str(data)))
        return {'id': '123'}

    def _uploadImages(self, images):
        ims = []
        for im_url in images:
            try:
                im, typ = self.im_tool.download(im_url)
                new_url = self.im_tool.upload(im, typ)
            except Exception as e:
                new_url = im_url
                print('{} in {} replace error'.format(im_url, self.url))
            ims.append(new_url)
            time.sleep(random.random())
        return ims





#sp = Spider()
#u = 'https://www.laohu8.com/post/910366938'
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/abc.html')
#data = sp.getHtmlByUrl(u)
#sp.parseSsPi(data)
#sp.parseDataLaohu(data)

def test1():
    sp = Spider()
    sp.debug = True
    url = 'https://mp.weixin.qq.com/s/kyEyjo170LwWjGpfSuqKDQ'
    data = sp.getHtmlByUrl(url)
    sp.parseWechat(data)

def test2():
    sp = Spider()
    sp.debug = True
    url = 'https://mp.weixin.qq.com/s/kyEyjo170LwWjGpfSuqKDQ'
    url = 'https://mp.weixin.qq.com/s/YfR__qVd9BtUvmaJDDDzqA'
    url = 'https://mp.weixin.qq.com/s/BgLO51KH9jeQC3DdZAYEgw'
    data = sp.getHtmlByUrl(url)
    sp.parseWechat(data)

def test3():
    sp = Spider()
    sp.debug = True
    url = 'https://mp.weixin.qq.com/s/kyEyjo170LwWjGpfSuqKDQ'
    url = 'https://mp.weixin.qq.com/s/YfR__qVd9BtUvmaJDDDzqA'
    url = 'https://mp.weixin.qq.com/s/Bgm2ZEmizrH5JrEcm8wFIg'
    data = sp.getHtmlByUrl(url)
    sp.parseWechat(data)

def test4():
    sp = Spider()
    sp.debug = True
    url = 'https://mp.weixin.qq.com/s/kyEyjo170LwWjGpfSuqKDQ'
    url = 'https://mp.weixin.qq.com/s/YfR__qVd9BtUvmaJDDDzqA'
    url = 'https://mp.weixin.qq.com/s/Bgm2ZEmizrH5JrEcm8wFIg'
    url = 'https://mp.weixin.qq.com/s/BgLO51KH9jeQC3DdZAYEgw'
    data = sp.getHtmlByUrl(url)
    sp.parseWechat(data)

import threading

threads = []
threads.append(threading.Thread(target=test1))
threads.append(threading.Thread(target=test2))
threads.append(threading.Thread(target=test3))
threads.append(threading.Thread(target=test4))


if __name__ == '__main__':
    for t in threads:
        t.start()