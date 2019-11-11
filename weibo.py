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

class WeiboSpider():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
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

