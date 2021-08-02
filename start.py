# coding=utf-8
# author:xsl


from cel import getWechat

def asynGetWechat(url):
    print("start asynGetWechat")
    resultA = getWechat.delay(url)
    print(resultA.successful())



if __name__ == '__main__':
    url = "https://mp.weixin.qq.com/s?src=11&timestamp=1625623201&ver=3175&signature=*Cswelwc1rN6ZJJcXzLqNDJC0cnYb-SrYc*TCk5MwHutZsprHumE3YN9EV6Y0zoFSXtkw0Zd2Z4FD7K4P08qFa4Rm-ooxzK8ULo48y3angJZLquA--g9Q-9zIJ1o3Qxt&new=1"

    asynGetWechat(url)
