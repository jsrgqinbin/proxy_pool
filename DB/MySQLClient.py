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
        self.password = password
        self.name = name
        if MySQLClient._pool is None:
            self.initPool(host, port)

    @staticmethod
    def initPool(host, port):
        MySQLClient._pool = PooledDB(creator=pymysql, host=host, port=port, user=USER, passwd=PASSWD, db=DB)
        try:
            MySQLClient._pool.connection()
        except Exception:
            exit("Unable to get connections from MySQL")

    def changeTable(self, name):
        self.name = name

    def put(self, proxy_obj, num=1):
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proxy,info_json FROM %s where proxy='%s'" % (self.name, proxy_obj.proxy))
        results = cursor.fetchall()
        try:
            if len(results) > 0:
                if self.name is "raw_proxy":
                    conn.cursor().execute("update %s set info_json='%s' where proxy='%s')" % (self.name, proxy_obj.info_json, proxy_obj.proxy))
                else:
                    conn.cursor().execute("update %s set info_json='%s',`count`=`count`+1 where proxy='%s')" % (self.name, proxy_obj.info_json, proxy_obj.proxy))
            else:
                if self.name is "raw_proxy":
                    conn.cursor().execute("INSERT INTO %s(proxy,info_json) VALUES ('%s','%s')" % (self.name, proxy_obj.proxy, proxy_obj.info_json))
                else:
                    conn.cursor().execute("INSERT INTO %s(proxy,info_json,`count`) VALUES ('%s','%s',%d)" % (self.name, proxy_obj.proxy, proxy_obj.info_json, num))
            conn.commit()
        # 插入重复的proxy
        except pymysql.err.IntegrityError:
            conn.close()
        conn.close()

    def delete(self, key):
        conn = MySQLClient._pool.connection()
        conn.cursor().execute("DELETE FROM %s WHERE proxy='%s'" % (self.name, key))
        conn.commit()
        conn.close()

    def pop(self):
        """
        弹出一个代理, 只对raw_proxy表使用
        :return: dict {proxy: value}
        """
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proxy FROM %s LIMIT 0,1" % self.name)
        conn.commit()
        result = cursor.fetchone()
        data = None
        if result is not None:
            self.delete(result[0])
            data = {"proxy": result[0]}
        conn.close()
        return data

    def getAll(self):
        """
        获取所有代理, 只对useful_proxy表使用
        :return: dict {proxy: value, proxy: value, ...}
        """
        data = {}
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proxy,info_json FROM %s" % self.name)
        conn.commit()
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(result[1])
        conn.close()
        return data

    def exists(self, key):
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proxy FROM %s WHERE proxy='%s'" % (self.name, key))
        conn.commit()
        if cursor.fetchone() is None:
            conn.close()
            return False
        conn.close()
        return True

    def getNumber(self):
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM %s" % self.name)
        conn.commit()
        result = cursor.fetchone()[0]
        conn.close()
        return result

    def clear(self):
        conn = MySQLClient._pool.connection()
        cursor = conn.cursor()
        cursor.execute("truncate table %s" % self.name)
        conn.commit()
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


if __name__ == '__main__':
    c = MySQLClient('useful_proxy', 'localhost', 3306)
    print(c.pop())
