from flask import Flask, request, abort, redirect, render_template
from urllib.parse import unquote
from datetime import datetime, timedelta
from collections import deque, defaultdict

from url import beautiful_url
from dao import add as add_note, get as get_note, del_note, get_all
import config


def dq():
    """
    对deque包装一下，产生指定默认长度的dq

    :return:
    """
    return deque(maxlen=config.fault_tolerant)


def get_dq_dict():
    return defaultdict(dq)


# flask app
app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")

# 在delta时间内出错次数小于等于fault_tolerant，允许访问
max_delta = timedelta(**config.ip_time_delta)  # 恢复访问时间

# 密码错误记录ip访问的时间
ip_wrong_request_date_dict = get_dq_dict()

# 浏览器主动请求的一些链接，被视为安全的，但不对请求进行功能实现
save_url = {
    'favicon.ico'
}


@app.route('/<password>')
def auth(password):
    """
    将密码操作写在这一个函数中，包括ip限制等，所有其他逻辑不再掺和密码和ip，ok，舒服了

    :param password: 密码
    :return:
    """
    # 当前访问ip
    ip = request.remote_addr
    # 访问限制

    wrong_time_list = ip_wrong_request_date_dict[ip]
    # 队列已满，说明连续错误次数已达标
    if len(wrong_time_list) == config.fault_tolerant:
        # 将当前时间对比第一次记录时间，而不是最后一次时间
        delta = datetime.today() - wrong_time_list[0]
        # 间隔时间小于max_delta，拒绝访问
        if delta < max_delta:
            abort(403)
        # 间隔时间大于等于max_delta，限制访问时间已结束

    # 浏览器主动请求的链接，不算做破译尝试
    if password in save_url:
        return password

    # 密码正确
    if password == config.password:
        # 清空该ip的错误记录
        wrong_time_list.clear()
        # 返回正确的http请求
        return show()
    # 密码错误
    now = datetime.today()
    # 访问时间添加上当前时间
    wrong_time_list.append(now)
    return 'password wrong!'


def show():
    """
    逻辑和展示，当然还可以重构，只不过现在功能简单，就先这样

    :return:
    """
    note = request.args.get('note', None)
    del_date = request.args.get('del_date', None)

    if del_date is not None:
        del_date = unquote(del_date)
        del_note(del_date)
        return redirect(f'/{config.password}')

    if note is not None:
        note = unquote(note)
        add_note(note)
        return redirect(f'/{config.password}')

    rows = get_all() if 'all' in request.args else get_note()
    rows = [
        (beautiful_url(row[0]), row[1])
        for row in reversed(rows)
    ]

    return render_template('font.html', rows=rows, password=config.password)


app.run(host=config.ip, port=config.port)
