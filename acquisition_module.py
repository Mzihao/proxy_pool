# -*- coding:UTF-8 -*-

"""
获取模块的逻辑相对简单，首先需要定义一个 Crawler 来从各大网站抓取代理。

为了实现灵活，在这里我们将获取代理的一个个方法统一定义一个规范，
如统一定义以 crawl 开头，这样扩展的时候只需要添加 crawl 开头的方法即可。
这些方法都定义成了生成器，通过 yield 返回一个个代理。
get_proxies()方法，将所有以 crawl 开头的方法调用一遍，获取每个方法返回的代理并组合成列表形式返回。 
"""


import json
from lxml import etree
import requests
from pyquery import PyQuery as pq


# 将所有含有crawl_的方法加入attrs['__CrawlFunc__']属性中
class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):  # 调用所有以crawl开头的方法
            print('成功获取代理', proxy)
            proxies.append(proxy)
        return proxies

    def crawl_daili66(self, page_count=22):
        urls = list()
        for i in range(1, page_count + 1):
            start_url = 'http://www.66ip.cn/areaindex_' + str(i) + '/1.html'
            urls.append(start_url)
        for url in urls:
            html = requests.get(url).text
            doc = pq(html)
            trs = doc('.containerbox table tr:gt(0)').items()
            for tr in trs:
                ip = tr.find('td:nth-child(1)').text()
                port = tr.find('td:nth-child(2)').text()
                # print(':'.join([ip,port]))
                yield ':'.join([ip, port])

    '''def crawl_goubanjia(self):
        headers = {
            'host': 'www.goubanjia.com',
            'Referer': 'http: // www.goubanjia.com /',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }
        start_url = 'http://www.goubanjia.com/'
        html= requests.get(start_url,headers = headers).text
        doc = pq(html)
        tds = doc('td.ip').items()
        for td in tds:
            td.find('p').remove()
            #print(td.text().replace('\n',''))
            yield td.text().replace('\n','')'''


if __name__ == '__main__':
    p = Crawler()
    p.crawl_daili66()
