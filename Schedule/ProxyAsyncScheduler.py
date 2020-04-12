# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/8/5: ProxyScheduler
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys
import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.append('../')

from Manager import ProxyManager
from Util import LogHandler
from Config.ConfigGetter import config
from Util.scrapeProxies import *
from Util.utilFunction import verifyProxyFormat
from ProxyHelper import Proxy


class AsyncDoFetchProxy(ProxyManager):
    """ fetch proxy"""

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('fetch_proxy')

    async def fetch_free_proxy_list_net(self):
        """
        fetch proxy into db by ProxyGetter
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        proxy_set = set()
        self.log.info("ProxyFetch : fetch_free_proxy_list_net start")
        self.log.info("ProxyFetch - {func}: start".format(func="fetch_free_proxy_list_net"))
        try:
            proxy_list = await scrape_free_proxy_list_net()
            if proxy_list is not None:
                for proxy in proxy_list:
                    proxy = proxy.strip()
                    if not proxy or not verifyProxyFormat(proxy):
                        self.log.error('ProxyFetch - {func}: {proxy} illegal'.format(func="fetch_free_proxy_list_net", proxy=proxy.ljust(20)))
                        continue
                    elif proxy in proxy_set:
                        self.log.info('ProxyFetch - {func}: {proxy} exist'.format(func="fetch_free_proxy_list_net", proxy=proxy.ljust(20)))
                        continue
                    else:
                        self.log.info('ProxyFetch - {func}: {proxy} success'.format(func="fetch_free_proxy_list_net", proxy=proxy.ljust(20)))
                        self.db.put(Proxy(proxy, source="fetch_free_proxy_list_net"))
                        proxy_set.add(proxy)
        except Exception as e:
            self.log.error("ProxyFetch - {func}: error".format(func="fetch_free_proxy_list_net"))
            self.log.error(str(e))
            self.log.error(traceback.format_exc())

    async def fetch_spys_one(self):
        """
        fetch proxy into db by ProxyGetter
        :return:
        """
        proxy_set = set()
        self.db.changeTable(self.raw_proxy_queue)
        self.log.info("ProxyFetch : start")
        self.log.info("ProxyFetch - {func}: start".format(func="fetch_spys_one"))
        try:
            proxy_list = await scrape_spys_one()
            if proxy_list is not None:
                for proxy in proxy_list:
                    proxy = proxy.strip()
                    if not proxy or not verifyProxyFormat(proxy):
                        self.log.error('ProxyFetch - {func}: {proxy} illegal'.format(func="fetch_spys_one", proxy=proxy.ljust(20)))
                        continue
                    elif proxy in proxy_set:
                        self.log.info('ProxyFetch - {func}: {proxy} exist'.format(func="fetch_spys_one", proxy=proxy.ljust(20)))
                        continue
                    else:
                        self.log.info('ProxyFetch - {func}: {proxy} success'.format(func="fetch_spys_one", proxy=proxy.ljust(20)))
                        self.db.put(Proxy(proxy, source="fetch_spys_one"))
                        proxy_set.add(proxy)
        except Exception as e:
            self.log.error("ProxyFetch - {func}: error".format(func="fetch_spys_one"))
            self.log.error(str(e))
            self.log.error(traceback.format_exc())

    def main_free_proxy_list_new(self):
        self.log.info("start fetch free_proxy_list_new proxy")
        asyncio.run(self.fetch_free_proxy_list_net())
        self.log.info("finish fetch free_proxy_list_new proxy")

    def main_spys_one(self):
        self.log.info("start fetch main_spys_one proxy")
        asyncio.run(self.fetch_spys_one())
        self.log.info("finish fetch main_spys_one proxy")


def free_proxy_list_net_scheduler():
    AsyncDoFetchProxy().main_free_proxy_list_new()


def spys_one_scheduler():
    AsyncDoFetchProxy().main_spys_one()


def runAsyncScheduler():
    # asyncProxyFetchScheduler()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(free_proxy_list_net_scheduler, 'interval', minutes=5)
    scheduler.add_job(spys_one_scheduler, 'interval', minutes=5)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    spys_one_scheduler()
