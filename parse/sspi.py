# coding=utf-8
# author:xsl
# 少数派

import re
from lxml import etree
from datetime import datetime
import json
from utils import fix_text



def sspi_parse(data):
    cont = re.findall(r'window.__INITIAL_STATE__=(.*?);\(function\(\){var', data)
    cont = cont[0]
    cont = json.loads(cont)
    post = cont.get('post')
    art = post.get('articleInfo')

    title = art.get('title')
    author = art.get('author').get('nickname')
    author_idf = str(art.get('author').get('id'))

    pub_at = art.get('released_time')
    pub_at = datetime.utcfromtimestamp(int(pub_at)) 

    con = art.get('body')
    html = etree.HTML(con)
    images = html.xpath('//img/@src')
    
    original_id = str(art.get('id'))
    url = 'https://sspai.com/post/'+original_id

    con = con.replace('<html><head></head><body>', '')
    con = con.replace('</body></html>', '')

    res = {
        "title": title,
        "content": con,
        "original_url": url,
        "original_id": str(original_id),
        "author": author ,
        "author_idf": str(author_idf),
        "published_at": pub_at,
        "created_at": datetime.utcnow(),
        "type": 'sspi',
        "original_images": images
    }
    return res
