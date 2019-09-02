# coding=utf-8
# author:xsl

import requests
import json
import re
import pymongo
import datetime
import time
import random
from lxml import etree
from utils import ImageTool

def fix_text(some):
    some = ''.join(some)
    some = some.strip()
    return some

class WechatSpider():

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
        client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        db = client['instance_db']
        self.art_col = db.article



    def getWechatByUrl(self, url):
        response = self.session.get(url, headers=self.headers)
        data = response.text
        html = etree.HTML(data)

        date = re.findall(r'ct\s*=\s*\"[0-9]*\"', data)
        if len(date) > 0:
            date = date[0]
        date = re.findall(r'\"[0-9]*\"', date)[0]
        date = date[1:-1]
        times = datetime.datetime.fromtimestamp(int(date))
        
        
        title = html.xpath('//h2[@id="activity-name"]/text()')
        title = ''.join(title)
        title = title.strip()
#        print(title)

        author = html.xpath('//span[@id="js_author_name"]/text()')
        author = ''.join(author)
        author = author.strip()
#        print(author)

        wx_name = html.xpath('//a[@id="js_name"]/text()')
        wx_name = fix_text(wx_name)
#        print(wx_name)

        meta_content = html.xpath('//div[@id="meta_content"]')
        author2 = author
        if len(meta_content) > 0:
            meta_content = meta_content[0]
            author2 = meta_content.xpath('./span[contains(@class, "rich_media_meta_text")]//text()')
            author2 = fix_text(author2)
            author2 = author2.replace(' ','')
            author2 = author2.replace('\n','')
#            print(author2)

        wx_info = html.xpath('//div[@class="profile_inner"]/p[@class="profile_meta"]')

        info1 = wx_info[0]
        info_title = info1.xpath('./label/text()')
        info_title = fix_text(info_title)

        info_value1 = info1.xpath('./span/text()')
        info_value1 = fix_text(info_value1)

#        print(info_title+": "+info_value1)

        info1 = wx_info[1]
        info_title = info1.xpath('./label/text()')
        info_title = fix_text(info_title)

        info_value = info1.xpath('./span/text()')
        info_value = fix_text(info_value)

#        print(info_title+": "+info_value)

        content1 = html.xpath('//div[@id="js_content"]')[0]

        content = etree.tostring(content1,encoding="utf8", pretty_print=True, method="html")
        content = content.decode('utf-8')
        content = re.sub(r' style=\"(.*?)\"', "", content)
        content = re.sub(r'<p><br></p>', "", content)
        content = re.sub(r'<p><span><br></span></p>', "", content)

            #    print(content)
        #content = re.sub(r'<(.*?)>', '', content)
    


        images = html.xpath('//img/@data-src')
#        print(images)
        ims = []
        for im_url in images:
            im, typ = self.im_tool.download(im_url)
            n_url = self.im_tool.upload(im, typ)
            ims.append(n_url)
            wwait = random.random()
            time.sleep(wwait)

        trans_cont = content
        i = 0
        for im_url2 in images:
            myimurl = ims[i]
            re_url1 = "data-src=\"" + im_url2 + "\""
            re_url2 = "src=\"" + im_url2 + "\""
            my_re = "src=\"" + myimurl + "\""
            trans_cont = trans_cont.replace(re_url1, my_re)
            trans_cont = trans_cont.replace(re_url2, my_re)
            i += 1


        content = re.sub(r'<(.*?)>', '', content)

#        print(content1)
        sa = {
            "title": title,
            "content": content,
            "transcoding": trans_cont,
            "original_url": url,
            "original_id": "",
            "author": wx_name+' '+author ,
            "author_idf": info_value1,
            "published_at": times,
            "created_at": datetime.datetime.utcnow(),
            "type": 'wechat',
            "images": ims
        }
        inid = self.art_col.insert_one(sa).inserted_id
        return {'id':str(inid)}
 

