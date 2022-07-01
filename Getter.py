# -*- coding:UTF-8 -*-

"""
Getter类:
动态地调用所有以 crawl 开头的方法，
然后获取抓取到的代理，将其加入到数据库存储起来。
"""

from db import RedisClient
from acquisition_module import Crawler

# 表示代理池的最大数量
POOL_UPPER_THRESHOLD = 10000


class Getter:
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        判断是否达到代理池限制
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)
