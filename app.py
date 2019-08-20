# coding=utf-8
# author:xsl

from flask import Flask, request
from .weibo import WeiboSpider

app = Flask(__name__)
app.config['PORT'] = 5001
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



@celery.task
def getWeibo(url):
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

if __name__ == '__main__':
    app.run(port=5001)

