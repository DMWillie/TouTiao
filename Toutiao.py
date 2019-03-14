"""
    作者:北辰
    日期:12/03/2019
    功能:爬取今日头条美图(以王昱珩为例),并将图片保存到本地
    版本:1.0
"""
import re
from datetime import datetime
import os
import requests
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

KEYWORD = '王昱珩'
def get_page(offset):
    """
    根据偏移量获取Ajax页面
    """
    params = {
        'aid':24,
        'app_name':'web_search',
        'offset':offset,
        'format':'json',
        'keyword':KEYWORD,
        'autoload':'true',
        'count':20,
        'en_qc':1,
        'cur_tab':1,
        'from':'search_tab',
        'pd':'synthesis'
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    """解析页面,提取每条数据的image_list字段中的每一张图片链接,将
    图片链接和图片所属的标题一并返回
    """
    if json.get('data'):
        for item in json.get('data'):
            try:
                title = item.get('title')
                images = item.get('image_list')
                for image in images:
                    yield{
                        'image':image.get('url'),
                        'title':title
                    }
            except TypeError:
                pass

def save_image(item):
    """
    保存图片,根据item的title来创建文件夹,然后请求这个图片链接,
    获取图片的二进制数据,以二进制的形式写入文件
    """
    dir_path = "C:\\Users\\HY\\Pictures\\爬虫\\"+KEYWORD+"\\"
    # 这一步将可能存在的不合法文件路径名变成合法的
    legal_title = re.sub('[\//\:\*\?\"\<\>\|\.]','_',item.get('title'))
    legal_path = dir_path + legal_title
    if not os.path.exists(legal_path):
        os.mkdir(legal_path)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            # 图片的名称使用其内容的MD5值,这样可以去除重复
            file_path = legal_path+'/{0}.{1}'.format(md5(response.content).hexdigest(),
                                             'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print('Already Downloaded',file_path)
    except requests.ConnectionError:
        print('Failed to Save Image')

def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print('正在保存图片')
        save_image(item)


GROUP_END = 20

if __name__ == '__main__':
    pool = Pool() #多线程的线程池
    groups = ([x*20 for x in range(GROUP_END+1)])
    time_start = datetime.now()
    pool.map(main,groups) #利用多线程的map()方法实现多线程下载
    pool.close()
    pool.join()
    time_end = datetime.now()
    time = (time_end - time_start).total_seconds()
    print("下载时间为:{}秒".format(time))
