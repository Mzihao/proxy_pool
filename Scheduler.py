# -*- coding:UTF-8 -*-
import time
import multiprocessing
from interface import app
from Getter import Getter
from Tester import Tester

TESTER_CYCLE = 20
GETTER_CYCLE = 20
TESTER_ENABLED = True
GTTER_ENABLED = True
API_ENABLED = True


class Scheduler():
    """
    调度器
    """
    def schedule_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        """
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """
        开启api
        """
        app.run()

    def run(self):
        print('代理池开始运行')
        if TESTER_ENABLED:
            tester_process = multiprocessing.Process(target=self.schedule_tester)
            tester_process.start()

        if GTTER_ENABLED:
            getter_process = multiprocessing.Process(target=self.schedule_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = multiprocessing.Process(target=self.schedule_api)
            api_process.start()


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
