# -*- coding:UTF-8 -*-
from db import RedisClient
from flask import Flask, g

__all__ = ['app']
app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis

@app.route('/')
def index():
    return '<h2>欢迎来到代理池</h2>'


@app.route('/random')
def get_proxy():
    """
    随机获取一个代理
    :return: 随机一个代理
    """
    conn = get_conn()
    return conn.random()


@app.route('/count')
def get_count():
    """
    获取代理池总量
    :return: 数量
    """
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run()