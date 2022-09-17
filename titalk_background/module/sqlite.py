from beartype import beartype
import pandas as pd
import sqlite3
import hashlib
import datetime

def today_time():
    datetime_dt = datetime.datetime.today() # 獲得當地時間
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")  # 格式化日期
    return datetime_str

class sqlTool:

    def __init__(self):
        self.cur = {}
        self.conn = {}
        self.user_info = 'user_info'

    @beartype
    def md5(self, string: str):
        md = hashlib.md5()
        md.update(string.encode('utf-8'))

        return md.hexdigest()

    @beartype
    def open_user_info_connection(self):
        db_name = './manager.db'
        timeout = 30000
        conn = sqlite3.connect(db_name,
                               isolation_level=None,
                               check_same_thread=False,
                               timeout=timeout)

        cur = conn.cursor()

        # 確認 table 是否存在
        cur.execute(f'CREATE TABLE IF NOT EXISTS {self.user_info}'
                    f'(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    f'username TEXT, password TEXT, create_time TEXT)')
        conn.commit()

        self.cur[self.user_info] = cur
        self.conn[self.user_info] = conn

    @beartype
    def open_article_connection(self, table_name):
        db_name = './manager.db'
        timeout = 30000
        conn = sqlite3.connect(db_name,
                               isolation_level=None,
                               check_same_thread=False,
                               timeout=timeout)

        cur = conn.cursor()

        # 確認 table 是否存在
        cur.execute(f'CREATE TABLE IF NOT EXISTS {table_name}'
                    f'(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    f'title TEXT, content TEXT, create_time TEXT, state TEXT, md5_key TEXT)')
        conn.commit()

        self.cur[table_name] = cur
        self.conn[table_name] = conn

    @beartype
    def create_table(self, table_name: str):
        db_name = './manager.db'
        timeout = 30000
        conn = sqlite3.connect(db_name,
                               isolation_level=None,
                               check_same_thread=False,
                               timeout=timeout)

        cur = conn.cursor()

        # 確認 table 是否存在
        cur.execute(f'CREATE TABLE IF NOT EXISTS {table_name}'
                    f'(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    f'title TEXT, content TEXT, create_time TEXT, state TEXT, md5_key TEXT)')
        conn.commit()

    # @beartype
    # def close_connection(self):
    #
    #     self.cur.close()
    #     self.conn.close()

    @beartype
    def insert_user_info(self, username: str, password: str):

        self.open_user_info_connection()
        df = pd.DataFrame({'username': [username],
                           'password': [password],
                           'create_time': [today_time()]
                           })

        df.to_sql(self.user_info, self.conn.get(self.user_info), if_exists='append', index=False)
        # self.close_connection()

    @beartype
    def insert_article(self, table_name: str, title: str, content: str):
        md5_key = self.md5(title + content)
        self.open_article_connection(table_name)
        df = pd.DataFrame({'title': [title],
                           'content': [content],
                           'create_time': [today_time()],
                           'md5_key': [md5_key],
                           'state': ['0'],
                           })

        df.to_sql(table_name, self.conn.get(table_name), if_exists='append', index=False)
        # self.close_connection()

    @beartype
    def select_article(self, table_name, state: str):

        sql = '''
        SELECT * 
        FROM {}
        WHERE `state` = {}
        LIMIT 10
        '''
        sql = sql.format(table_name, state)
        self.open_article_connection(table_name)

        df = pd.read_sql(sql, self.conn.get(table_name))
        df_dict = df.to_dict('records')

        # self.close_connection()

        return df_dict

    @beartype
    def crawler_select_article(self, table_name: str, md5_key: str):

        sql = '''
        SELECT * 
        FROM {}
        WHERE `md5_key` = "{}"
        LIMIT 10
        '''
        sql = sql.format(table_name, md5_key)
        self.open_article_connection(table_name)

        df = pd.read_sql(sql, self.conn.get(table_name))
        df_dict = df.to_dict('records')

        # self.close_connection()

        return df_dict

    @beartype
    def select_latest_article(self, table_name):

        sql = '''
        SELECT * 
        FROM {}
        WHERE state = "0"
        LIMIT 10
        '''
        sql = sql.format(table_name)
        self.open_article_connection(table_name)

        df = pd.read_sql(sql, self.conn.get(table_name))
        df_dict = df.to_dict('records')

        # self.close_connection()

        return df_dict

    @beartype
    def update_article_state(self, table_name: str, state: str, md5_key: str):
        sql = '''
        UPDATE {}
        SET `state` = "{}"
        WHERE `md5_key` = "{}"
        '''
        sql = sql.format(table_name, state, md5_key)
        self.open_article_connection(table_name)
        self.cur.get(table_name).execute(sql)
        self.conn.get(table_name).commit()

    @beartype
    def update_all_article_state(self, table_name):
        sql = '''
        UPDATE {}
        SET `state` = "0"
        WHERE `state` = "1"
        '''
        sql = sql.format(table_name)
        self.open_article_connection(table_name)
        self.cur.get(table_name).execute(sql)
        self.conn.get(table_name).commit()

    @beartype
    def select_user_info(self, username: str):

        sql = '''
        SELECT * 
        FROM {}
        WHERE `username` = "{}"
        LIMIT 1
        '''
        sql = sql.format(self.user_info, username)
        self.open_user_info_connection()

        df = pd.read_sql(sql, self.conn.get(self.user_info))
        df_dict = df.to_dict('records')

        # self.close_connection()

        return df_dict

    @beartype
    def update_user_info(self, username: str, password: str):
        sql = '''
        UPDATE {} 
        SET password = "{}"
        WHERE username = "{}"
        '''
        sql = sql.format(self.user_info, password, username)
        self.open_user_info_connection()
        self.cur.get(self.user_info).execute(sql)
        self.conn.get(self.user_info).commit()

        # self.close_connection()


if __name__ == '__main__':
    username = 'jojobot123'
    password = '123qwe'
    title = '測試內容'
    content = '12345qwef'
    table_name = ''
    # create_time = [today_time()]
    DB = sqlTool()
    DB.open_article_connection(table_name)
    df_dict = DB.select_article(table_name=table_name, state='0')
    # DB.insert_article(title, content)
