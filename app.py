# coding=utf-8
# author:xsl

from flask import Flask, request
from flask_cors import CORS
from weibo import WeiboSpider
from celery import Celery

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
    print(data)
    return data

@celery.task(bind=True)
def getWeiboo(self, url):
    sp = WeiboSpider()
    d = sp.getWeiboByUrl(url)
    return d

@app.route('/weibo', methods=['POST'])
def weibo():
    data = request.get_json()
    print('acb')
    print(data)
    url = data.get('url')
    res = getWeibo.delay(url)
    return {'id': str(res.id)}

if __name__ == '__main__':
    app.run(port=5001)
