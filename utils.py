# coding=utf-8
# author:xsl

import os
import hashlib
import requests
from qcloud_cos import CosConfig, CosS3Client


class ImageTool():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
 
        self._init_cos()
        self.baseUrl = 'http://shilin-1255431184.cos.ap-beijing.myqcloud.com/'

    def _init_cos(self):
        secret_id = os.environ.get('COS_SECRET_ID') or ''
        secret_key = os.environ.get('COS_SECRET_KEY') or ''
        region = 'ap-beijing'
        token = None
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)
        self.client = CosS3Client(config)


    def _fileMD5(self, file):
        md5obj = hashlib.md5()
        md5obj.update(file)
        hash = md5obj.hexdigest()
        return str(hash)

    def download(self, url):
        resp = self.session.get(url, headers=self.headers)
        content = resp.content
        mime_type = resp.headers['Content-Type']
        return (content, mime_type)

    def upload(self, image, mime_type='jpg'):
        file_name = self._fileMD5(image)
        file_name = 'spider/'+file_name
        resp = self.client.put_object(
                    Bucket='shilin-1255431184',
                    Body=image,
                    Key=file_name,
                    StorageClass='STANDARD',
                    ContentType=mime_type
                )
        return self.baseUrl + file_name


#url = 'https://img-blog.csdnimg.cn/20190102174111248.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MTgxNzAzNA==,size_16,color_FFFFFF,t_70'

#imT = ImageTool()

#im, typ = imT.download(url)
#imurl = imT.upload(im, typ)
#print(imurl)
