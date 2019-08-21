# coding=utf-8
# author:xsl

from pymongo import MongoClient
import datetime

dbCli = MongoClient('mongodb://localhost:27017/')
db = dbCli['instance_db']

data = {
        'title': '疑似王丽坤新恋情', 
        'content': '林更新王丽坤分手了？？网曝王丽坤和一名男子亲密合照，还说二人是恋人。这是真的吗？ ', 
        'original_url': 'aaasshttps://m.weibo.cn/detail/4407664438402073',
        'original_id': '4407664438402073', 
        'author': '星综屏影', 
        'author_idf': '5612278337', 
        'create_at': datetime.datetime.utcnow(),
        'source': 'weibo', 
        'images': [
            'https://wx3.sinaimg.cn/orj360/0067OxYlly1g672dhhrpmj30en0atgmm.jpg', 'https://wx1.sinaimg.cn/orj360/0067OxYlly1g672dhp988j30f20dn3zy.jpg', 'https://wx3.sinaimg.cn/orj360/0067OxYlly1g672dhy99mj30dw09mwfa.jpg', 'https://wx3.sinaimg.cn/orj360/0067OxYlly1g672di915hj30fd09kdg6.jpg', 'https://wx4.sinaimg.cn/orj360/0067OxYlly1g672dik7ayj30m80zkdhh.jpg', 'https://wx3.sinaimg.cn/orj360/0067OxYlly1g672divdr8j30mu0xcdgk.jpg', 'https://wx2.sinaimg.cn/orj360/0067OxYlly1g672dkd734j31jk15rb2a.jpg', 'https://wx4.sinaimg.cn/orj360/0067OxYlly1g672dkw7ohj30u013w7du.jpg', 'https://wx2.sinaimg.cn/orj360/0067OxYlly1g672do04u1j34c64avnph.jpg']}

article = db.article
print(article.find_one({"original_url": "https://m.weibo.cn/detail/4407664438402073"}))

inid = article.insert_one(data).inserted_id
print(inid)
