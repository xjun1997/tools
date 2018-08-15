import requests
import pymysql
import pymssql
import traceback
import time

class Timer(object):
    """
    计时器，对于需要计时的代码进行with操作：
    with Timer() as timer:
        ...
        ...
    print(timer.cost)
    ...
    """
    def __init__(self, start=None):
        self.start = start if start is not None else time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop = time.time()
        self.cost = self.stop - self.start
        return exc_type is None

class MySql(object):
    """
    MySql工具类
    """
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def get_connect(self):
        if not self.db:
            raise (NameError, '没有设置数据库信息')
        conn = pymysql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset='utf8')
        if conn.cursor():
            return conn
        else:
            raise (NameError, '连接数据库失败')

    def exec_query(self, sql):
        """
        :param sql:查询sql
        :return: 查询操作
        """
        conn = self.get_connect()
        cur = conn.cursor()
        cur.execute(sql)
        res_list = cur.fetchall()

        # 单线程查询完毕后必须关闭连接
        conn.close()
        return res_list

    def exec_non_query(self, sql):
        """
        单次增删改操作，适用于某些不想多次操作的场景
        :param sql: 非查询sql
        :return: 操作结果
        """
        conn = self.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception:
            print(sql)
            print('提交sql失败')
            print(traceback.format_exc())
            return False
        finally:
            conn.close()

    def exec_safety_non_query(self, sql):
        """
        安全的非查询操作
        :param sql: 非查询sql
        :return: 操作结果
        """
        conn = self.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            try:
                print(sql)
                print("提交sql失败，重新提交中...")
                cur.execute(sql)
                conn.commit()
                return True
            except Exception as e:
                print('提交sql失败，报错原因为%s,请检查sql代码' % e)
                print(traceback.format_exc())
                return False

class SqlServer(object):
    """
    SqlServer工具类
    """
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def get_connect(self):
        if not self.db:
            raise (NameError, '没有设置数据库信息')
        conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset='utf8')
        if conn.cursor():
            return conn
        else:
            raise (NameError, '连接数据库失败')

    def exec_query(self, sql):
        """
        :param sql:查询sql
        :return: 查询操作
        """
        conn = self.get_connect()
        cur = conn.cursor()
        cur.execute(sql)
        res_list = cur.fetchall()

        # 单线程查询完毕后必须关闭连接
        conn.close()
        return res_list

    def exec_non_query(self, sql):
        """
        单次增删改操作，适用于某些不想多次操作的场景
        :param sql: 非查询sql
        :return: 操作结果
        """
        conn = self.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception:
            print(sql)
            print('提交sql失败')
            print(traceback.format_exc())
            return False
        finally:
            conn.close()

    def exec_safety_non_query(self, sql):
        """
        安全的非查询操作
        :param sql: 非查询sql
        :return: 操作结果
        """
        try:
            conn = self.get_connect()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            return True
        except pymssql.IntegrityError as error:
            print('主键冲突，sql操作失败:', error)
            print(sql)
        except Exception as e:
            try:
                print(sql)
                print("提交sql失败，重新提交中...")
                cur.execute(sql)
                conn.commit()
                return True
            except Exception as e:
                print('提交sql失败，报错原因为%s,请检查sql代码' % e)
                print(traceback.format_exc())
                return False


"""解析请求头"""
def format_headers(string):
    """
    将在Chrome上复制下来的浏览器UA格式化成字典，以\n为切割点
    :param string: 使用三引号的字符串
    :return:
    """
    string = string.strip().replace(' ', '').split('\n')
    dict_ua = {}
    for key_value in string:
        dict_ua.update({key_value.split(':')[0]: key_value.split(':')[1]})
    return dict_ua


"""解析URL"""
from urllib.parse import unquote
def format_parameter(request_url):
    """
    格式化url并返回接口链接与格式化后的参数
    :param request_url:请求链接
    :return:接口链接，格式化后的参数
    """
    assert isinstance(request_url, str)
    para_dict = {}
    _ = [para_dict.update({p.split('=')[0]:p.split('=')[1]}) for p in unquote(request_url).split('?')[1].split('&')]
    return request_url.split('?')[0], para_dict

"""请求循环"""
def request(url):
    while True:
        try:
            resp = requests.get(url, headers=headers, timeout=30, verify=False)
        except Exception as error:
            print(url,error)
            time.sleep(20)
            resp = ''
            request(url)
        if resp:
            break
    return resp