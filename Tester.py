from db import RedisClient
import aiohttp
from botocore import exceptions
import time
import asyncio

VALID_STATUS_CODES = [200]  # 成功响应状态码
TEST_URL = 'https://www.baidu.com'  # 检测的站点
BATCH_TEST_SIZE = 100


class Tester(object):
    """
    检测代理
    """

    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """
        检测单个代理
        :param proxy: Proxy object
        :return:
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用')
                    else:
                        self.redis.decrease(proxy)
                        print('代理不可用', proxy)
            except (exceptions.ClientError, TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理不可用', proxy)

    def run(self):
        """
        测试主函数
        :return:
        """
        print('开始测试！')
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('测试出现错误', e.args)


if __name__ == '__main__':
    t = Tester()
    t.run()
