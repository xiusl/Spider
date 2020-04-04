# coding=utf-8
# author:xsl

import re
from lxml import etree
from datetime import datetime
from utils import fix_text

def obj_at_idx(arr, idx):
    try:
        d = arr[idx]
    except Exception as e:
        d = ''
    return d

def wx_parse(data):

    html = etree.HTML(data)

# 文章发表时间
    date = re.findall(r'ct\s*=\s*\"[0-9]*\"', data)
    if len(date):
        date = date[0]

    date = re.findall(r'\"[0-9]*\"', date)[0]
    date = date[1:-1]
    date_int = datetime.utcfromtimestamp(int(date))

# 文章标题
    title = html.xpath('//h2[@id="activity-name"]/text()')

# 公众号名
    wx_name = html.xpath('//a[@id="js_name"]/text()')
    
# 编辑/作者
    editor = html.xpath('//div[@id="meta_content"]/span[contains(@class, "rich_media_meta_text")]/text()')
    editor = obj_at_idx(editor, 0)
    
# 微信号+介绍
    wx_info = html.xpath('//div[@class="profile_inner"]/p[@class="profile_meta"]/span/text()')
    wx_code = obj_at_idx(wx_info, 0)
    wx_desc = obj_at_idx(wx_info, 1)

# 正文
    content1 = html.xpath('//div[@id="js_content"]')[0]
    # 删除一些空行，样式等
    content = etree.tostring(content1, encoding="utf8", pretty_print=True, method="html")
    content = content.decode('utf-8')
    content = re.sub(r' style=\"(.*?)\"', "", content)
    content = re.sub(r'<p><br></p>', "", content)
    content = re.sub(r'<p><span><br></span></p>', "", content)

# 图片
    images = html.xpath('//div[@id="js_content"]//img/@data-src')
    
    res = {
        "title": fix_text(title),
        "content": content,
        "original_id": "",
        "author": fix_text(wx_name)+'/'+fix_text(editor) ,
        "author_idf": fix_text(wx_code),
        "published_at": date_int,
        "type": 'wechat',
        "original_images": images
    }
    return res
    print(res)

def test():
    file = open('/Users/tmt/abc.html')
    d = file.read()
    wx_parse(d)

if __name__ == '__main__':
    test()
