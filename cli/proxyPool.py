# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy_pool
   Description :
   Author :        JHao
   date：          2019/8/2
-------------------------------------------------
   Change Activity:
                   2019/8/2:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys
import click
import platform
sys.path.append('../')

from Config.setting import HEADER
from Schedule.ProxyScheduler import runScheduler
from Schedule.ProxyAsyncScheduler import runAsyncScheduler
from Api.ProxyApi import runFlask, runFlaskWithGunicorn
os.environ['TZ'] = 'Asia/Shanghai'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='2.0.0')
def cli():
    """ProxyPool cli工具"""


@cli.command(name="schedule")
def schedule():
    """ 启动调度程序 """
    click.echo(HEADER)
    runScheduler()


@cli.command(name="schedule_async")
def schedule():
    """ 启动调度程序 """
    click.echo(HEADER)
    runAsyncScheduler()


@cli.command(name="webserver")
def schedule():
    """ 启动web服务 """
    click.echo(HEADER)
    if platform.system() == "Windows":
        runFlask()
    else:
        runFlaskWithGunicorn()


if __name__ == '__main__':
    cli()
