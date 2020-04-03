# coding=utf-8
# author:xsl


import re
from lxml import etree
from datetime import datetime
import json
from utils import fix_text



def jianshu_parse(data):
    html = etree.HTML(data)

    a = html.xpath('//script[@type="application/json"]/text()')
    a = fix_text(a)

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
    pub = datetime.utcfromtimestamp(int(pub))

    trans_cont = free_content
    
    e_cont = etree.HTML(trans_cont)
    images = e_cont.xpath('//img/@data-original-src')
    images = ['http:'+im for im in images]
    
    res = {
        "title": title,
        "content": free_content,
        "original_id": str(ori_id),
        "author": author ,
        "author_idf": str(author_id),
        "published_at": pub,
        "created_at": datetime.utcnow(),
        "type": 'jianshu',
        "original_images": images
    }
    return res