# coding=utf-8
# author:xsl

from flask import Flask, request
from flask_cors import CORS
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


@app.route('/')
def index():
    return "暗号：落霞与孤鹜齐飞"

# @app.route('/weibo', methods=['POST'])
# def weibo():
#     data = request.get_json()
#     url = data.get('url')
#     res = getWeibo.delay(url)
#     return {'id': str(res.id)}

@app.route('/wechat', methods=['POST'])
def wechat():
    data = request.get_json()
    url = data.get('url')
    res = getWechat.delay(url)
    return {'id':"12312"}

@app.route('/kr36', methods=['POST'])
def kr36():
    data = request.get_json()
    url = data.get('url')
    res = get36Kr.delay(url)
    return {'id':"12312"}

@app.route('/laohu', methods=['POST'])
def laohu():
    data = request.get_json()
    url = data.get('url')
    res = getLaohu.delay(url)
    return {'id':"12312"}

@app.route('/jianshu', methods=['POST'])
def jianshu():
    data = request.get_json()
    url = data.get('url')
    res = getJianshu.delay(url)
    return res


@app.route('/sspi', methods=['POST'])
def sspi():
    data = request.get_json()
    url = data.get('url')
    res = getSsPi.delay(url)
    return res

@app.route('/spider', methods=['POST'])
def spider():
    data = request.get_json()
    url = data.get('url')
    res = {'res': 'nono'}
    if 'sspai' in url:
        res = getSsPi.delay(url)
    elif '36kr' in url:
        res = get36Kr.delay(url)
    elif 'weixin' in url:
        res = getWechat.delay(url)
    elif 'laohu' in url:
        res = getLaohu.delay(url)
    elif 'jianshu' in url:
        res = getJianshu.delay(url)
    return {'res': 'ok'}

# @celery.task
# def getWeibo(url):
#     sp = WeiboSpider()
#     data = sp.getWeiboByUrl(url)
#     return data

@celery.task
def getWechat(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseWechat(data)
    return res

@celery.task
def get36Kr(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseData36kr(data)
    return res

@celery.task
def getLaohu(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseDataLaohu(data)
    return res

@celery.task
def getJianshu(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseJianShu(data)
    return res

@celery.task
def getSsPi(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseSsPi(data)
    return res

if __name__ == '__main__':
    app.run(port=5001)

