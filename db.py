# -*- coding:UTF-8 -*-
import redis
from random import choice


MAX_SCORE = 100  # 最大分数
MIN_SCORE = 0  # 最小分数
INITIAL_SCORE = 10  # 初始分数
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies'  # 键名


class RedisClient(object):
    """
    代理池连接redis客户端
    """

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: redis地址
        :param port: redis端口
        :param password: redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理, ip:port, 形式类似 8.8.8.8:88
        :param score: 分数（整型）
        :return: 添加结果
        """
        if not self.db.zscore(REDIS_KEY, proxy):  # zscore查找并返回成员的分数
            return self.db.zadd(REDIS_KEY, score, proxy)  # 如果不存在，则添加，并设置初始分数

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果最高分数不存在，则按排名获取,否则抛出异常
        :return: 代理, ip:port, 形式类似 8.8.8.8:88
        """
        # 尝试获取最高分数代理
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)  # zrangebyscore返回指定区间的成员列表
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)  # zrevrange递减排序，（从大到小排序）
            if len(result):
                return choice(result)
            else:
               raise Exception("代理池为空！")

    def decrease(self, proxy):
        """
        代理减一分, 如果分数小于最小值则被删除
        :param proxy: 代理
        :return: 修改后的分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理',proxy,'当前分数',score,'减1')
            return self.db.zincrby(REDIS_KEY, proxy, -1)  # zincrby分数修改
        else:
            print('代理',proxy,'当前分数',score,'移除')
            return self.db.zrem(REDIS_KEY, proxy)  # zrem移除

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) is None  # 查询是否存在，存在返回true

    def max(self, proxy):
        """
        将代理设置为100分
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        """
        获取代理数量
        :return: 数量（整型int）
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)