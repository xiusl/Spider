# coding=utf-8
# author:xsl

import os
from celery import Celery
from spider import Spider

RDS_PWD = os.getenv('RDS_PWD')
RDS_HOST = os.getenv('RDS_HOST')


CELERY_BROKER_URL = 'redis://:{0}@{1}:6379/1'.format(RDS_PWD, RDS_HOST)
CELERY_RESULT_BACKEND = 'redis://:{0}@{1}:6379/2'.format(RDS_PWD, RDS_HOST)
CELERY_NAME = 'spider'

print(CELERY_BROKER_URL)


app = Celery(CELERY_NAME, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@app.task
def getWechat(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseWechat(data)
    return res


@app.task
def get36Kr(url):
    sp = Spider()
    data = sp.getHtmlByUrl(url)
    res = sp.parseData36kr(data)
    return res

