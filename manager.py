# coding=utf-8
# author:xsl

from flask import Flask, request
from flask_cors import CORS
from weibo import WeiboSpider
from wechat import WechatSpider
from celery import Celery

application = Flask(__name__)
application.config['PORT'] = 5001
application.config['DEBUG'] = True
application.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
application.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(application.name, broker=application.config['CELERY_BROKER_URL'])
celery.conf.update(application.config)

CORS(application, supports_credentials=True)

@celery.task
def getWeibo(url):
    sp = WeiboSpider()
    data = sp.getWeiboByUrl(url)
    print(data)
    return data

@celery.task(bind=True)
def getWeiboo(self, url):
    sp = WeiboSpider()
    d = sp.getWeiboByUrl(url)
    return d

@application.route('/weibo', methods=['POST'])
def weibo():
    data = request.get_json()
    print('acb')
    print(data)
    url = data.get('url')
    res = getWeibo.delay(url)
    return {'id': str(res.id)}


@celery.task
def getWechat(url):
    sp = WechatSpider()
    d = sp.getWechatByUrl(url)
    return d

@application.route('/wechat', methods=['POST'])
def wechat():
    data = request.get_json()
    url = data.get('url')
    res = getWechat.delay(url)
    return {'id': str(res.id)}

@application.route('/test')
def test():
    return {'res': 'ok'}

#if __name__ == '__main__':
#    application.run(port=5001)

