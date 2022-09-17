from flask import Flask, render_template
from flask import request, session, redirect, url_for
from flask_session import Session
from module.mysql_tools import MysqlTools
from functools import wraps
from render_html import *
from redis import Redis

db = MysqlTools()
Pool = db.db_config()

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6380)

app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = "jojo"
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 36000
Session(app)

admit_ls = []

alert = """

"""

def checkSession(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        sess = session.get("session")
        if sess is None:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    table_name = 'account_management'
    if request.method == 'POST':
        username = request.values.get('username')
        password = request.values.get('password')

        if any([username == '', password == '']):
            err = '帳號密碼不得為空值'
            return render_template('login_error.html', err=err)

        # 驗證帳號是否存在
        result = db.check_acc_pas_exists(Pool, table_name, username)
        if bool(result) is False:
            err = '帳號密碼錯誤'
            return render_template('login_error.html', err=err)

        elif bool(result) is True:
            db_password = result[2]
            if password != db_password:
                err = '帳號密碼錯誤'
                return render_template('login_error.html', err=err)

        # 最高管理權限顯示此頁面
        elif username in admit_ls:
            return render_template('admit_article.html')

        session['session'] = 'session'
        # return redirect(url_for('article_submit'))
        option_value = option_value_dict.get(username)
        return render_template('article_submit.html', option_value=option_value)

    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return redirect(url_for('login'))

# 文章提交
@app.route('/article_submit', methods=['GET', 'POST'])
@checkSession
def article_submit():
    if request.method == 'GET':
        return render_template('article_submit.html')

    if request.method == 'POST':
        table_name = request.form.get('table_name')
        add_title = request.form.get('add_title')
        add_content = request.form.get('add_content')
        try:
            db.insert_article_data(Pool, table_name, add_title, add_content, "0")
        except:
            return render_template('article_submit.html', result=add_article_success_result)

        return render_template('article_submit.html', result=add_article_success_result)


@app.route('/add_manager', methods=['GET', 'POST'])
def add_manager():
    if request.method == 'GET':
        return render_template('add_manager.html')

    elif request.method == 'POST':
        username = request.values.get('add_username')
        password = request.values.get('add_password')

        result = db.select_user_info(username)
        if bool(result) is False:
            db.insert_user_info(username, password)
            return render_template('add_manager.html', result=add_manager_success_result)
        else:
            return render_template('add_manager.html', result=add_manager_warning_result)


@app.errorhandler(404)
def page_not_found(e):
    sess = session.get("session")
    if sess is None:
        return redirect(url_for('login'))

    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
