# coding=utf-8
# author:xsl

from flask import Flask, request
from flask_cors import CORS
from weibo import WeiboSpider
from wechat import WechatSpider
from celery import Celery
from spider import Spider

app = Flask(__name__)
app.config['PORT'] = 5001
app.config['DEBUG'] = True
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

CORS(app, supports_credentials=True)

@celery.task
def getWeibo(url):
    sp = WeiboSpider()
    data = sp.getWeiboByUrl(url)
    return data

@celery.task(bind=True)
def getWeiboo(self, url):
    sp = WeiboSpider()
    d = sp.getWeiboByUrl(url)
    return d

@app.route('/weibo', methods=['POST'])
def weibo():
    data = request.get_json()
    url = data.get('url')
    res = getWeibo.delay(url)
    return {'id': str(res.id)}


@celery.task
def getWechat(url):
    sp = WechatSpider()
    d = sp.getWechatByUrl(url)
    return d

@app.route('/wechat', methods=['POST'])
def wechat():
    data = request.get_json()
    url = data.get('url')
    res = getWechat.delay(url)
    return {'id': str(res.id)}

@celery.task
def get36Kr(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.paraseData36kr(data)
    return res

@app.route('/kr36', methods=['POST'])
def kr36():
    data = request.get_json()
    url = data.get('url')
    res = get36Kr.delay(url)
    return res

if __name__ == '__main__':
    app.run(port=5001)

