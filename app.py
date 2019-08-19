# coding=utf-8
# author:xsl

from flask import Flask, request
from .weibo import WeiboSpider

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



@celery.task
def getWeibo(url):
    data = sp.getWeiboByUrl(url)


@app.route('/weibo', methods=['POST'])
def weibo():
    data = request.get_json()
    url = data.get('url')
    getWeibo.delay(url)
    return {'ok': 1}

if __name__ == '__main__':
    app.run(port=5001)

