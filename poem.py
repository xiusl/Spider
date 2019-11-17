# coding=utf-8
# author:xsl

import requests
import json
import pymongo
import datetime
import time
import random
import os
from lxml import etree
from utils import ImageTool


class Spider():

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Content-Type': 'charset=utf8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
        }
        self._init_db()
        #self.im_tool = ImageTool()
        self.ex = ['axing', 'bxing', 'cxing', 'dxing', 'exing', 'langsongAuthor', 'langsongAuthorPY', 
            'pinglunCount', 'beijingIspass', 'shangIspass', 'yizhuIspass', 'yizhuYuanchuang']

        self.count = 50
        
    def _init_db(self):
        mongo_url = 'mongodb://127.0.0.1:27017'
        client = pymongo.MongoClient(mongo_url)
        db = client['poem_db']
        self.db = db

    def _fixText(self, text):
        new_t = ''.join(text)
        return new_t.strip()

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    def getHtmlByUrl(self, url):
        self.url = url
        proxy = self.get_proxy().get('proxy')
        proxies = {"http": "http://{}".format(proxy)}
        try:
            response = self.session.get(url, headers=self.headers, verify=False, proxies=proxies)
            data = response.content
            response.encoding = "utf-8"
        except:
            print(url)
            return "123"
        return data

    def getHtmlByFile(self, path):
        f = open(path, 'r')
        data = f.read()
        return data

    def _uploadImages(self, images):
        ims = []
        for im_url in images:
            im, typ = self.im_tool.download(im_url)
            new_url = self.im_tool.upload(im, typ)
            ims.append(new_url)
            wait = random.random()
            print('download ok %s' % new_url)
            time.sleep(wait)
        return ims

    def paraseAuthor(self, data):
        html = etree.HTML(data)
        
        sons = html.xpath('//div[@class="sonspic"]')
        for s in sons:
            name = s.xpath('./div/p/a/b/text()')
            name = self._fixText(name)

            url = s.xpath('./div/div[@class="divimg"]/a/@href')
            url = self._fixText(url)

            cover = s.xpath('./div/div[@class="divimg"]/a/img/@src')
            cover = self._fixText(cover)
            
            d = {'name':name, 'o_url': url, 'cover': cover} 
            self.save(d)

    def save(self, data):
        print(data)
        aut = self.db.author_a
        a = aut.find_one({'nameStr': data['nameStr']})
        if a:
            print('exsit')
        else:
            ins_id = aut.insert_one(data).inserted_id
            print(ins_id)

    def parase(self, data):
        data = data.decode('utf-8')
        d = json.loads(data)
        
        li = d.get('authors')
        for l in li:
            self.save(l)

    def parase2(self, data):
        data = data.decode('utf-8')
        d = json.loads(data)
        self.count = d.get('sumCount') or 50
        li = d.get('tb_gushiwens')
        for l in li:
            a = l
            for b in self.ex:
                if b in a.keys():
                    a.pop(b)
            self.save2(a)

    def save2(self, data):
        aut = self.db.poem_a
        a = aut.find_one({'idnew': data['idnew']})
        if a:
            print('exsit')
        else:
            ins_id = aut.insert_one(data).inserted_id
            print(ins_id)

    def ss(self):
        b_url = 'http://app.gushiwen.cn/api/author/Default10.aspx?token=gswapi&page='
        for i in range(1, self.count / 10):
            url = b_url+str(i)
            data = self.getHtmlByUrl(url)
            self.parase(data)
            wait = random.random()
            time.sleep(1+wait)

    def ss2(self, uid):
        #uid = '6888D54DC01ADF87C8193C8ED94E9BFE'
        b_url = 'https://app.gushiwen.cn/api/author/authorsw11.aspx?token=gswapi&id='+uid+'&page='
        for i in range(1, self.count / 10):
            url = b_url+str(i)
            print(url)
            data = self.getHtmlByUrl(url)
            self.parase2(data)
            wait = random.random()
            time.sleep(wait)

    def ss3(self):
        aut = self.db.author_a
        ds = aut.find()
        ids = []
        oids = ['093669487C72BD84435F143F68BF046F', '82D05FF9D9F0D41DD41E55538CF7189C', 'FBCFE1890CACB8F7EB7B256BA59B1CE5', 'BEBE109AF8FF2265B697BB2CBA6B207A', '9FB16195D3B84E5A9D694AD50C34653B', '84E7506A3A96517250EC3720CDC30B74', '297F46C42041016639CDE4ADA41B3B82', 'C3803DBDE772CFCA1E9AC93172536C22', 'E918723CE7165E51CC7618566FAC8E48', '901C8DEBD646032DA267CDC51EC4BF8A', 'DFA0F4DE479E39DE68129489A6DF273F', '12A738BA27A8B0EDC44B5A6CB54F68BE', '050104B30A7AD0834067BAD3650651E0', 'DA53E597340EBE1638C769F95BB139A5', 'E7FBEADC53A0811A87EA245107650CAA', '88EA0E0BA17AB9DE644E1430EE659878', 'AB897BBAA650A8A7618680F6AB5F3345', 'D05FCCC2AFFC036DF4A60621288AAEC8', '4909ED62B5F255E259D2E6051AFEF6E9', 'ED80FD3556E208D66D78A3EB4D6C2B2B', 'CC0824ACF7D7C74198B6F7DDC9CB331E', '11FE3E5F82F93511828840FF06F343DF', '242F6E133EC0E246767B46BF0625DC0D', 'BE4C204A6093886192FCFE7B6C7EC665', '10C83F209F74D70C4E404631EC421D2B', '943CEF77039626DABE4F4B5A9601B0C3', '1ADC1EA6931100587ED2DF05523A890C', 'C3850AA2CFF3FA40C4EB23E11F60AC67', 'AE609F38C5DE2195841BB3052A271B54', 'C26ED96A6BB8C14DD276A9EB444D95E7', 'ECD881F29BB479F257CA66B123FEF844', '860DBE26BCD6C7A1D87B4DCDD4F7936E', '1B90CBE0FA7B80FD70B19C5FD87053E1', 'D147B8511EF43A6B1CE431F4A436C670', 'DF100CA300DC96B26D7D629D3AB0EE20', 'FAA26339D53E6DD39B31365E818DB588', 'C22B0A56A7684CD971261427C13570FC', '104D40C4CB9CD133DA9DBBD43F5425BB', '3C3C61728342AEF95B39206489877A9B', 'C31AADCB4E4962EA0F9842516BB3DC0B', '66A8D65983435757D6370B0690E8EBBA', '2968493B3DACA2BA050682F3DBB83B73', '1DCED700DFD5CCA0DE33CDFD8DDBF709', '9B06935C0C8ADFE50190F3A9A2D94D0A', '152F0F37B6D80868CF572024C6ABD7FE', 'CBBAE5027700FBB41E599FE8A0318C59', 'D95CFCE5B1FDA9E49AFAA0D4EBA5C131', '4ED9343A6A2893C0E6186D9ADE35EC4C', '3421A02E8EA522477D502E0B825FA69B', '0D8A4E4CB8DE9BA7ABDF2F1452A16210', 'D515D1943D54389780F071D133E44CF9', 'E7FD2717B8C21607C11B408AAD0B3D28', '5948E71FC908853EDAEE8FFC096868A6', 'FB5C3BC08B60B69378FCA5D806C04E76', 'F71341F53976913112DDB051433E9B3B', '6A4E2BA4E19FC44E10F26D9C36651290', '0F9463C6D3288E1E1766D8F629FB102E', 'A6C8B54B782CD5391ED9AA1FAF886340','A0AF523FF9476A09BC3D8D6DAB878F80', '57CDE02305AE75F7824FF0C59F4B49A9', 'BFB6BDEE5F07EE25E9FAF01ED50BFF4B', '9DA8B4B9C2010B140FB7DEC5A62BFB82', 'CDE4D896F3AADFD4170D348C234172A6', '7F7104AACCFFE8CD4B52F7D8E6BB4DA8', 'C1494E2DCB7451A9FB9496CD78152639', '9592AC10860D50DA180B2A86401CCD8D', 'BCB3C3C94A74E774BE8DDF31A571073F', 'E4383C08A54DB648BFC5A898DBE5AC88', 'A5C6DDE8B5DF7C84304B2E2D3A0712F8', 'EA2A01B80DC715EAAC3FA3BB292B611B', 'BAF90BB26612DC0BEA142DFE05F310D2', 'DA5CF215546557E7D1CBFD5EA36DD085', '9705BE104381DF1D175F95A46CFEBE5B', '7B0A3D928A096C555DD77429FC621062', '81C1F27C2BC1F37727A303077D70EC98', 'C73DD98221FC95099E2FD1283061AD30', '6BD6017DA5DDA68C9A2596B79DBA8B93', 'FD65DBAFCF0A73C8880EF859707F0C2B', '2AA087E2C67A8E2A6C4B76D852AC4A8A', '40D8BC5091AFAF2C59F76AA513BA750F', '06198343881B2AD4E7BCF196FB27297C', '4B78526492B84960A45AB25AF3FD9558', 'F388A5A6CBC3F741A1E00C46DF83D437','98908E58EA4AE54DE08EDCD12ED09BAF', 'F5A0FCC0295C1C6816FC7E3151BD1D6E', '3344A992F3D523C161FAEEDFFCA2F6EC', '8B354D14E714FE9D45EA8684F4BFA880','6888D54DC01ADF87C8193C8ED94E9BFE', 'ACED84F2F3C2DEE0868E66E2F9DB18F4', '6911E98663CC56F9099A93D520AA2373', '19D5441382902DEA28FCFC1BB339B6FC', '37E32BAC4B670CF3DD527F1283C55042', '2B0F6E397BC8C61FE7A5DDBEFFC4A9C1', 'D97000E67A4E671D1D6EA5139B213765', '463BCE18212081C858CD02E3A8A51ED7', '29DCCC0D633A647C3707C8FBACB98BC3', '62BDA354811022A967718F87D53E8A57', '7D96E28ADE5BB3C02EE18A8DE47BA04F', '8D23D4EFC54F72C2385F0DF98A17F5A2', '5A157AEC67B3D27369B9F3E972CBCD1B']
        for d in ds:
            idd = d.get('idnew')
            if idd in oids:
                continue
            print(ids)
            self.ss2(idd)
            ids.append(idd)
            wait = random.random()
            time.sleep(wait)



# https://so.gushiwen.org/authors/

sp = Spider()
#data = sp.getHtmlByFile('/Users/xiusl/Desktop/b.htm')
#sp.paraseAuthor(data)
sp.ss3()

