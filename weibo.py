# coding=utf-8
# author:xsl

import requests
import urllib
import urllib.parse
import json
import base64, rsa, binascii
import datetime
import time
import re
import os
import pymongo
from weibo_config import Config
from utils import ImageTool
from lxml import etree

class WeiboSpider():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1'
        }
        mongo_url = os.getenv('MONGO_URL') or 'mongodb://127.0.0.1:27017'
        client = pymongo.MongoClient(mongo_url)
        self.db = client['instance_db']
        self.im_tool = ImageTool()

    def _pre_login(self, account, password):
        headers = self.headers
        pre_login_url = 'https://login.sina.com.cn/sso/prelogin.php?'

        su = base64.b64encode(account.encode(encoding='utf-8'))

        Config.pre_login_params['su'] = su
        
        pre_params = Config.pre_login_params
        pre_login_url = pre_login_url + urllib.parse.urlencode(pre_params)

        response = self.session.get(pre_login_url, headers=headers, verify=False)
        result = response.text[response.text.find('(')+1:-1]
        data = json.loads(result)

        data['su'] = su
        print('pre login success')
    
        return data
        
    def login(self, account, password):
        data = self._pre_login(account, password)
        
        pubkey = data.get('pubkey')
        servertime = data.get('servertime')
        nonce = data.get('nonce')
        rsapbk = int(pubkey, 16)
        key = rsa.PublicKey(rsapbk, 65537)
        msg = str(servertime) + '\t' + str(nonce) + '\n' +  str(password)

        sp = binascii.b2a_hex(rsa.encrypt(msg.encode('utf-8'), key))

        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'

        login_params = Config.login_params
        login_params['su'] = data.get('su')
        login_params['sp'] = sp
        login_params['servertime'] = servertime
        login_params['nonce'] = nonce
        login_params['rsakv'] = data['rsakv']

        response = self.session.post(login_url, data=login_params, headers=self.headers, verify=False)
        redirect_urls = re.findall(r'https%3A%2F%2Fweibo.*retcode%3D0', response.text)
        if len(redirect_urls) <= 0:
            print('login error')
            return False

        redirect_url = redirect_urls[0]
        redir_url = urllib.parse.unquote(redirect_url)
        res = self.session.get(redir_url)
        cookie = json.dumps(self.session.cookies.get_dict())
        self.cookie = cookie
        print('login success')
        return True

    def getUserHome(self, user_id):
        url = "https://weibo.com/u/"+user_id+"?"
        params = {
            "pids": "Pl_Official_MyProfileFeed__20",
            "is_all": 1,
            "profile_ftype": 1,
            "page": 1,
            "ajaxpagelet": 1,
            "ajaxpagelet_v6": 1,
        }
        url = url + urllib.parse.urlencode(params)
        response = self.session.get(url, headers=self.headers, verify=False, timeout=60)
        with open("abc.txt",'w') as fw:
            fw.write(response.text)
        return self.parseWebHTML(response.text)

    def parseWebHTML(self, html):
        html = html.replace('<script>parent.FM.view(', '')
        html = html.replace(')</script>', '')

        json_html = json.loads(html)
        html = json_html.get('html')

        et = etree.HTML(html)
        details = et.xpath('//div[contains(@class, "WB_detail")]')


        des = []
        for de in details:

            info = de.xpath('./div[contains(@class, "WB_info")]/a/text()')
            username = ''.join(info).strip()

            text = de.xpath('./div[contains(@class, "WB_text")]/text()')
            text = ''.join(text).strip()

            created_at = de.xpath('./div[contains(@class, "WB_from")]/a/@date')
            created_at = ''.join(created_at).strip()
            created_at = datetime.datetime.fromtimestamp(int(created_at)/1000)

            ims = de.xpath('.//img/@src')
            fims = []
            for im in ims:
                if 'h5' in im:
                    continue
                if 'sinaimg.cn' in im:
                    fims.append(im)

            video = de.xpath('./div[contains(@class, "WB_media_wrap")]/div[@class="media_box"]/ul[contains(@class, "WB_media_a")]/li[contains(@class, "WB_video")]/@video-sources')
            video = ''.join(video).strip()
            video = urllib.parse.unquote(urllib.parse.unquote(video))
            video = video.split(',')
            if len(video) > 0:
                video = video[0]
                video = video.replace('fluency=', '')
            else:
                video = ''

            result = {
                "name": username,
                "text": text,
                "created_at": created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "images": fims,
                "video": video
            }
            des.append(result)


        with open('dd.json', 'w') as dw:
            dw.write(json.dumps(des, ensure_ascii=False, indent=4))

    def getWeiboByUrl(self, url):
        if "weibointl" in url:
            f_pars = urllib.parse.urlparse(url)
            f_que = f_pars.query
            f_d = urllib.parse.parse_qs(f_que)
            w_id = f_d.get('weibo_id')[0]
            url = 'https://m.weibo.cn/detail/'+ str(w_id)
        #cookie = "_ga=GA1.2.1005202506.1568940735; _T_WM=20813437200; SSOLoginState=1571102629; ALF=1573694629; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhadzuXAcR_n3vQEwXKCWU-5JpX5KMhUgL.FoqEehB0S020S0e2dJLoI0qLxK-LBKeLB-zLxKqL1--L1KMLxKBLB.eL1-2LxKqL1-eL1h.LxKML12eLB-zLxKML1-2L1hBt; SUHB=0P1MYm06KSwziP; MLOGIN=1"
        cookie = "_ga=GA1.2.1005202506.1568940735; SSOLoginState=1571102629; ALF=1573694629; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhadzuXAcR_n3vQEwXKCWU-5JpX5KMhUgL.FoqEehB0S020S0e2dJLoI0qLxK-LBKeLB-zLxKqL1--L1KMLxKBLB.eL1-2LxKqL1-eL1h.LxKML12eLB-zLxKML1-2L1hBt; SUHB=0P1MYm06KSwziP; MLOGIN=1"
        cookie_dict = {i.split("=")[0]:i.split("=")[-1] for i in cookie.split("; ")}
        print(cookie_dict)

        response = self.session.get(url, headers=self.headers, verify=False, timeout=60, cookies=cookie_dict)
        data = re.findall(r'render_data = ([\s\S]*?)\[0\] \|\| \{\};', response.text)
        status = json.loads(data[0])
        if len(status) > 0:
            status = status[0]
        status = status.get('status')
        user = status.get('user')
        pics = status.get('pics')
        p = []
        if pics:
            for d in pics:
                im_url = d.get('large').get('url')
                im, typ = self.im_tool.download(im_url)
                new_url = self.im_tool.upload(im, typ)
                p.append(new_url)
                time.sleep(1)

        content = re.sub(r'<(.*?)>', '', status.get('text'))

        pb_time = datetime.datetime.strptime(status.get('created_at'),'%a %b %d %H:%M:%S %z %Y')

        sa = {
            "title": status.get('status_title'),
            "content": content,
            "transcoding": content,
            "original_url": url,
            "original_id": status.get('mid'),
            "author": user.get('screen_name'),
            "author_idf": str(user.get('id')),
            "published_at": pb_time,
            "created_at": datetime.datetime.utcnow(),
            "type": 'weibo',
            "images": p
        }
        article = self.db.article
        inid = article.insert_one(sa).inserted_id
        return {'id':str(inid)}


def test():
    url = "https://m.weibo.cn/detail/4427334087651512"
    sp = WeiboSpider()
    sp.login('xiushilin@sina.cn', 'Wb110120#')
    d = sp.getWeiboByUrl(url)
    print(d)

def test1():
    sp = WeiboSpider()
    sp.login("", "")
    sp.getUserHome('1950132797')
    f = open('abc.txt')
    sp.parseWebHTML(f.read())

def test2():
    sp = WeiboSpider()
    url = "http://m.weibo.cn/status/4427334087651512?display=0&retcode=6102"
    d = sp.getWeiboByUrl(url)
    print(d)

if __name__ == "__main__":
    test2()
