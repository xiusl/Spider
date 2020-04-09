# coding=utf-8
# author:xsl

import re
from lxml import etree
from datetime import datetime
from utils import fix_text
import json

def obj_at_idx(arr, idx):
    try:
        d = arr[idx]
    except Exception as e:
        d = ''
    return d

def zhihu_parse(data):

    html = etree.HTML(data)

    js_data = html.xpath('//script[@id="js-initialData"]/text()')
    d = json.loads(js_data[0])

    initialState = d.get('initialState')
    entities = initialState.get('entities')
    answers = entities.get('answers')
    answer_id = list(answers.keys())
    answer = answers.get(answer_id[0])

    author = answer.get('author')
    content = answer.get('content')
    question = answer.get('question')
    title = question.get('title')
    q_id = question.get('id')
    pub_at = answer.get('updatedTime')
    author_name = author.get('name')
    author_id = author.get('id')

    content = answer.get('content')
    
    ec = etree.HTML(content)

    images = ec.xpath('//img/@src')
    images = [im for im in images if im.startswith('http')]


    res = {
        "title": title,
        "content": content,
        "original_id": str(q_id) + '-' + str(answer_id[0]),
        "author": author_name,
        "author_idf": str(author_id),
        "published_at": datetime.utcfromtimestamp(pub_at),
        "original_images": images,
        "type": "zhihu"
    }

    return res

def test():
    file = open('/Users/tmt/Desktop/zhihu.html')
    d = file.read()
    zhihu_parse(d)

if __name__ == '__main__':
    test()
