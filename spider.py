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
from parse import (
    wx_parse,
    laohu_parse,
    kr36_parse,
    jianshu_parse,
    sspi_parse
)


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
        res = sspi_parse(data)
        
        images = res['original_images']
        ims = self._uploadImages(images)
        
        trans_cont = con
        for i, im_url in enumerate(images):
            n_url = ims[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+n_url+"\""
            trans_cont = trans_cont.replace(re_url,my_url)

        res['images'] = ims
        res['transcoding'] = trans_cont
        res['original_url'] = self.url
        self._save(res)
        return {'id':'123'}



    def parseData36kr(self, data):
        res = kr36_parse(data)

        images = res['original_images']
        my_images = self._uploadImages(images)
        trans_content = res['content']

        i = 0
        for im_url in images:
            new_url = my_images[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_cont = trans_content.replace(re_url,my_url)
            i += 1

        res['images'] = my_images
        res['transcoding'] = trans_content
        res['original_url'] = self.url

        self._save(res)
        return {'id':'123'}


    def parseJianShu(self, data):
        
        res = jianshu_parse(data)
        trans_content = res['content']
        
        images = res['original_images']
        my_images = self._uploadImages(images)

        for i, im_url in enumerate(images):
            new_url = my_images[i]
            re_url = "data-original-src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_content = trans_content.replace(re_url,my_url)

        res['images'] = my_images
        res['transcoding'] = trans_content
        res['original_url'] = self.url
        self._save(res)
        return {'id':'123'}


    def parseDataLaohu(self, data):
        res = laohu_parse(data)
        images = res['original_images']
        my_images = self._uploadImages(images)
        trans_content = res['content']

        i = 0
        for im_url in images:
            new_url = my_images[i]
            re_url = "src=\""+im_url+"\""
            my_url = "src=\""+new_url+"\""
            trans_content = trans_content.replace(re_url,my_url)
            i += 1

        res['images'] = my_images
        res['transcoding'] = trans_content
        res['original_url'] = self.url
        self._save(res)
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



def test():
    sp = Spider()
    sp.debug = True
    url = 'https://www.laohu8.com/news/2024497124'
    url = 'https://36kr.com/p/5308747'
    url = 'https://www.jianshu.com/p/3441e258fd83'
    url = 'https://sspai.com/post/59516'
    data = sp.getHtmlByUrl(url)
    # sp.parseData36kr(data)
    # sp.parseJianShu(data)
    sp.parseSsPi(data)

if __name__ == '__main__':
    test()