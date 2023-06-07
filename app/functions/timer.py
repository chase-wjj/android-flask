from flask import Blueprint, request, current_app
from flasgger import swag_from
from app.functions.account import login_required, identify
from app.functions.email_funcs import send_notice_email
from threading import Thread
import datetime
import time
import inspect
import ctypes


timer_bp = Blueprint('timer', __name__)


def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def reminder(app, hour, minute, message, username):
    with app.app_context():
        print(hour, minute, message, username)
        while True:
            now = datetime.datetime.now()
            if int(now.hour) == int(hour) and int(now.minute) == int(minute):
                print("mail sent")
                send_notice_email(message, username)
                time.sleep(60)
            time.sleep(1)


user_proc = {}


@timer_bp.route('/addTimer/', methods=['POST'])
@login_required
@swag_from('swagger/addTimer.yml')
def add_timer():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    schedule_time = body_data['schedule_time']
    schedule_message = body_data['schedule_message']  # 该参数为药物名

    print(schedule_time, schedule_message, username)
    sche_hour = schedule_time.split(':')[0]
    sche_minute = schedule_time.split(':')[1]

    if username in user_proc.keys():
        stop_thread(user_proc[username])

    user_proc[username] = Thread(target=reminder, args=(
        current_app._get_current_object(), sche_hour, sche_minute, schedule_message, username))
    user_proc[username].start()

    if username in user_proc.keys():
        return 'success', 201
    else:
        return 'error', 500


@timer_bp.route('/deleteTimer/', methods=['POST'])
@login_required
@swag_from('swagger/deleteTimer.yml')
def delete_timer():
    username = identify(request.headers.get("Authorization", default=None))
    if not (username in user_proc.keys()):
        return 'failed', 500
    stop_thread(user_proc[username])
    return 'success', 200
