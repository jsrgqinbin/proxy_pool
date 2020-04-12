# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：		MySQLClient.py
   Description:		封装MySQL操作
   Author:			Masazumi
   Contact:			masazumi_@outlook.com
   Date：			2018/7/22
   Comment:			建立数据库proxy，选择proxy执行mysql.sql，修改下面的账户配置
-------------------------------------------------
"""

__author__ = 'Masazumi'

DB = "proxy_pool"
USER = "proxy_pool"
PASSWD = "abc123"

import pymysql
from DBUtils.PooledDB import PooledDB


class MySQLClient(object):
    _pool = None

    def __init__(self, name, host, port, password):
        self.name = name
        self._pool = MyDb(host=host, port=port, username=USER, password=password, dbname=DB)

    def changeTable(self, name):
        self.name = name

    def put(self, proxy_obj, num=1):
        results = self._pool.getAllResult("SELECT proxy,info_json FROM %s where proxy='%s'" % (self.name, proxy_obj.proxy))
        try:
            if len(results) > 0:
                if self.name is "raw_proxy":
                    sql = "update %s set info_json='%s' where proxy='%s')" % (self.name, proxy_obj.info_json, proxy_obj.proxy)
                else:
                    sql = "update %s set info_json='%s',`count`=`count`+1 where proxy='%s')" % (self.name, proxy_obj.info_json, proxy_obj.proxy)
            else:
                if self.name is "raw_proxy":
                    sql = "INSERT INTO %s(proxy,info_json) VALUES ('%s','%s')" % (self.name, proxy_obj.proxy, proxy_obj.info_json)
                else:
                    sql = "INSERT INTO %s(proxy,info_json,`count`) VALUES ('%s','%s',%d)" % (
                        self.name, self._pool.escape_string(proxy_obj.proxy), self._pool.escape_string(proxy_obj.info_json), num)
            self._pool.insertOrUdateInfo(sql)
        # 插入重复的proxy
        except pymysql.err.IntegrityError:
            self._pool.close()

    def delete(self, key):
        self._pool.insertOrUdateInfo("DELETE FROM %s WHERE proxy='%s'" % (self.name, key))

    def pop(self):
        """
        弹出一个代理, 只对raw_proxy表使用
        :return: dict {proxy: value}
        """
        result = self._pool.getAllResult("SELECT proxy FROM %s LIMIT 0,1" % self.name)
        data = None
        if result is not None:
            self.delete(result[0])
            data = {"proxy": result[0]}
        return data

    def getAll(self):
        """
        获取所有代理, 只对useful_proxy表使用
        :return: dict {proxy: value, proxy: value, ...}
        """
        results = self._pool.getAllResult("SELECT proxy,info_json FROM %s" % self.name)
        data = []
        for result in results:
            data.append(result[1])
        return data

    def exists(self, key):
        result = self._pool.getSignleResult("SELECT proxy FROM %s WHERE proxy='%s'" % (self.name, key))
        if result is None:
            return False
        return True

    def getNumber(self):
        result = self._pool.getSignleResult("SELECT COUNT(*) FROM %s" % self.name)
        return result[0]

    def clear(self):
        self._pool.insertOrUdateInfo("truncate table %s" % self.name)
        return True

    def update(self, key, value):
        """
        未使用
        """
        pass

    def get(self, proxy):
        """
        未使用
        """
        pass


class MyDb:
    cursor = ''  # 句柄
    db = ''  # 打开数据库连接
    '''
        定义构造方法
        host：主机名
        username;用户名
        password:密码
        dbname:数据库名
        db:打开数据库连接
        cursor:获取游标句柄
    '''

    def __init__(self, host, port, username, password, dbname):
        self.port = port
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname

        self.db = pymysql.connect(host=self.host, port=self.port, user=self.username, password=self.password, database=self.dbname)
        self.cursor = self.db.cursor()

    def escape_string(self, key):
        return self.db.escape_string(key)

    # 获取所有的结果集
    def getAllResult(self, sql):
        self.db.ping(reconnect=True)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    # 获取所有的结果集
    def getSignleResult(self, sql):
        self.db.ping(reconnect=True)
        self.cursor.execute(sql)
        results = self.cursor.fetchone()
        return results

    # 插入或更新数据
    def insertOrUdateInfo(self, sql):
        try:
            # 执行SQL语句
            self.db.ping(reconnect=True)
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
        # 返回受影响的行数
        return self.cursor.rowcount

    def clear(self):
        self.db.ping(reconnect=True)
        self.cursor.execute("truncate table %s" % self.name)
        self.db.commit()
        return True

    # 关闭链接
    def close(self):
        self.db.close()


if __name__ == '__main__':
    c = MySQLClient('useful_proxy', 'localhost', 3306, 'abc123')
    print(c.pop())
