#!/usr/bin/env python3

import urllib.request
from bs4 import BeautifulSoup
import demjson
import threading
import os
from time import sleep
import requests

downdir = "D:\\Pictures\\pixiv\\"

requestSession = requests.session()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
      AppleWebKit/537.36 (KHTML, like Gecko) \
      Chrome/52.0.2743.82 Safari/537.36'  # Chrome on win10
requestSession.headers.update({'User-Agent': UA,'Referer':"http://www.pixiv.net/"})

phtml = urllib.request.urlopen("http://www.pixiv.net/").read()
soup = BeautifulSoup(phtml)
pjson = soup.find("input",attrs={"class": "json-data"})
pdejson = demjson.decode(pjson['value'])

class ErrorCode(Exception):
    '''自定义错误码:
        1: URL不正确
        2: URL无法跳转为移动端URL
        3: 中断下载'''
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return repr(self.code)

def __download_one_img(imgUrl,imgPath, callback):
    retry_num = 0
    retry_max = 2
    while True:
      try:
          downloadRequest = requestSession.get(imgUrl, stream=True, timeout=2)
          with open(imgPath, 'wb') as f:
              for chunk in downloadRequest.iter_content(chunk_size=1024):
                  if chunk: # filter out keep-alive new chunks
                      f.write(chunk)
                      f.flush()
          callback()
          break
      except (KeyboardInterrupt, SystemExit):
          print('\n\n中断下载，删除未下载完的文件！')
          if os.path.isfile(imgPath):
              os.remove(imgPath)
          raise ErrorCode(3)
      except:
          retry_num += 1
          if retry_num >= retry_max:
              raise
          print('下载失败，重试' + str(retry_num) + '次')
          sleep(2)

count = len(pdejson['pixivBackgroundSlideshow.illusts']['landscape'])
print('共计{}张图片'.format(count))
i = 1
downloaded_num = 0

def __download_callback():
    pass;
    #nonlocal downloaded_num
    #nonlocal count
    #downloaded_num += 1
    #print('\r{}/{}... '.format(downloaded_num, count), end='')

download_threads = []
for p in pdejson['pixivBackgroundSlideshow.illusts']['landscape']:
    imgPath = os.path.join(downdir , '{0:0>3}.jpg'.format(p['illust_id']) )
    i += 1
    if os.path.isfile(imgPath):
        count -= 1
        continue

    print(p['illust_id'])
    print(p['illust_title'])
    print(p['url']['1200x1200'])
    print(p['user_name'])
    print(p['profile_img']['main_s'])
    download_thread = threading.Thread(target=__download_one_img,
                                       args=(p['url']['1200x1200'], imgPath, __download_callback))
    download_threads.append(download_thread)
    download_thread.start()
[t.join() for t in download_threads]
print('完毕!\n')
