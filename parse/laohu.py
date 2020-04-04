# coding=utf-8
# author:xsl
# 老虎证券

import re
from lxml import etree
from datetime import datetime
from utils import fix_text


def laohu_parse(data):
    html = etree.HTML(data)
        
    title = html.xpath('//h1[@class="article-title"]/text()')

    author = html.xpath('//span[@class="article-author"]/a/text()')
    
    pub = html.xpath('//span[@class="article-date"]/text()')
    pub = fix_text(pub)
    pub = pub[2:]
    pub = datetime.strptime(pub, '%Y-%m-%d %H:%M')

    content = html.xpath('//div[@class="article-content"]')
    content = etree.tostring(content[0], encoding="utf8", pretty_print=True, method="html")
    content = content.decode('utf8')

    images = html.xpath('//div[@class="article-content"]//img/@src')
    
    res = {
        "title": fix_text(title),
        "content": content,
        "original_id": "",
        "author": fix_text(author),
        "author_idf": "",
        "published_at": pub,
        "type": 'laohu',
        "original_images": images
    }
    return res
