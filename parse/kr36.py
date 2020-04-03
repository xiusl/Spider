# coding=utf-8
# author:xsl


import re
from lxml import etree
from datetime import datetime
import json
from utils import fix_text



def kr36_parse(data):
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

    title = art_d.get('title')
    original_id = art_d.get('id')

    user = art_d.get('user')
    author = user.get('name')
    author_idf = user.get('id')
    pub_at = art_d.get('published_at')
    print(pub_at)
    pub_at = datetime.strptime(pub_at, '%Y-%m-%d %H:%M:%S')


    con = etree.HTML(content)
    images = con.xpath('//img/@src')

    
    res = {
        "title": fix_text(title),
        "content": content,
        "original_id": str(original_id),
        "author": fix_text(author),
        "author_idf": str(author_idf),
        "published_at": pub_at,
        "created_at": datetime.utcnow(),
        "type": '36kr',
        "original_images": images
    }
    return res