import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.join(PROJECT_DIR, os.pardir)

sys.path.append(PARENT_DIR)
sys.path.append(PROJECT_DIR)

MONGO_DB = os.getenv('MONGO_DB') or 'instance_db'
MONGO_URL = os.getenv('MONGO_URL') or 'mongodb://127.0.0.1:27017/instance_db'


SMS_ACCOUNT = os.getenv('SMS_ACCOUNT') or ''
SMS_TOKEN = os.getenv('SMS_TOKEN') or ''


SMS_TENC_ID = os.getenv('SMS_TENC_ID') or ''
SMS_TENC_KEY = os.getenv('SMS_TENC_KEY') or ''


COS_SECRET_ID = os.getenv("COS_SECRET_ID") or "123"
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY") or "456"


EMAIL_SMTP = 'smtp.exmail.qq.com'
EMAIL_SMTP_PORT = '465'
EMAIL_ADMIN = 'help@xiusl.com'
EMAIL_ADMIN_PWD = 'He110120.'


QINIU_ACCESS = os.getenv('QINIU_ACCESS')
QINIU_SECRET = os.getenv('QINIU_SECRET')