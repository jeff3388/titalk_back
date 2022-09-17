import pymysql
from DBUtils.PersistentDB import PersistentDB

class MysqlTools:

    ## MySQL 連線設定 ##
    def db_config(self):
        db_dict = {

        }

        POOL = PersistentDB(
            creator=pymysql,
            maxusage=None,
            setsession=[],
            ping=0,
            closeable=False,
            threadlocal=None,
            host=db_dict['MySql_IP'],
            port=db_dict['MySql_Port'],
            user=db_dict['MySql_account'],
            password=db_dict['MySql_password'],
            database=db_dict['MySql_db_name'],
            charset='utf8'
        )

        return POOL


    def select_data(self, POOL, table_name):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()
        SQL = '''
            SELECT *
            FROM {}
            WHERE `state`= "0"
            LIMIT 1
          '''
        SQL = SQL.format(table_name)
        try:
            with conn:
                cursor.execute(SQL)
                rows = cursor.fetchone()
                return rows
        except Exception as e:
            print(e)
            conn.rollback()

    def check_article_exists(self, POOL, table_name, title):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()

        SQL = '''
                SELECT *
                FROM {}
                WHERE `title`= "{}"
                LIMIT 1
              '''
        SQL = SQL.format(table_name, title)
        try:
            with conn:
                cursor.execute(SQL)
                rows = cursor.fetchone()
                return rows
        except Exception as e:
            print(e)
            conn.rollback()

    def check_acc_pas_exists(self, POOL, table_name, username):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()
        SQL = '''
                    SELECT *
                    FROM {}
                    WHERE `username`= "{}"
                    LIMIT 1
                  '''
        SQL = SQL.format(table_name, username)
        try:
            with conn:
                cursor.execute(SQL)
                rows = cursor.fetchone()
                return rows
        except Exception as e:
            print(e)
            conn.rollback()

    def insert_article_data(self, POOL, table_name, title, content, state):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()

        # 插入語法
        SQL = '''
            INSERT INTO {} 
            (title, content, state)
            VALUES ("{}","{}","{}")
            '''
        s = SQL.format(table_name, title, content, state)
        try:
            with conn:

                cursor.execute(s)
                conn.commit()  # 提交資料
        except Exception as e:
            print(e)
            conn.rollback()

    def insert_admin_info(self, POOL, table_name, username, password):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()

        # 插入語法
        SQL = '''
            INSERT INTO {} 
            (username, password)
            VALUES ("{}","{}")
            '''
        s = SQL.format(table_name, username, password)
        try:
            with conn:

                cursor.execute(s)
                conn.commit()  # 提交資料
        except Exception as e:
            print(e)
            conn.rollback()

    def update_data(self, POOL, table_name, Id=None):
        conn = POOL.connection(shareable=False)
        cursor = conn.cursor()
        SQL = '''
                UPDATE {}
                SET `state` = "1"
                WHERE `id`= {}
        '''

        # SQL = '''
        #             UPDATE article
        #             SET `state` = 0
        #             WHERE `state`= 1
        #     '''
        SQL = SQL.format(table_name, Id)
        try:
            with conn:
                cursor.execute(SQL)
                # cursor.execute(SQL)
        except Exception as e:
            print(e)
            conn.rollback()

if __name__ == '__main__':
    table_name = 'account_management'
    username = ''
    password = ''
    db = MysqlTools()
    Pool = db.db_config()

    result = db.check_acc_pas_exists(Pool, table_name, username)
    if bool(result) is False:
        db.insert_admin_info(Pool, table_name, username, password)
