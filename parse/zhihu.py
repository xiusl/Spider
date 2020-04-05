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

def wx_parse(data):

    html = etree.HTML(data)

    js_data = html.xpath('//script[@id="js-initialData"]/text()')
    d = json.loads(js_data[0])

    initialState = d.get('initialState')
    entities = initialState.get('entities')
    answers = entities.get('answers')
    answer = answers.get('1108807169')

    author = answer.get('author')
    content = answer.get('content')
    question = answer.get('question')
    title = question.get('title')
    q_id = question.get('id')
    pub_at = answer.get('updatedTime')
    print(author.get('name'))
    print(title)
    print(q_id)
    print(pub_at)


def test():
    file = open('/Users/xiusl/Desktop/zhihu.htm')
    d = file.read()
    wx_parse(d)

if __name__ == '__main__':
    test()
