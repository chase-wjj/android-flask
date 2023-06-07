from flask import Blueprint, request
from flask_mail import Message
from flasgger import swag_from
import random

from app.functions.database import db_add_verify_code, db_get_email_by_username
from app.extensions.extensions import mail

email_bp = Blueprint("email", __name__)


@email_bp.route('/sendVerifyEmail/', methods=['POST'])
@swag_from('swagger/sendVerifyEmail.yml')
def send_verify_email():
    body_data = request.json
    target_email = body_data['email']
    verify_code = ""
    for _ in range(0, 6):
        verify_code += str(random.randint(0, 9))
    status, res = db_add_verify_code(verify_code, target_email)
    if status is False:
        return res, 500
    msg = Message('协心力验证码', sender=('协心力', 'djk20@foxmail.com'), recipients=[target_email])
    msg.body = 'body'
    msg.html = '''
        <div>亲爱的协心力用户：</div>
        <div>&nbsp;&nbsp;您好！您的协心力验证码为''' + verify_code + '''，该验证码将在15分钟后失效，请您尽快填写，谢谢！</div>
        <div>&nbsp;</div>
        <div>协心力</div>
        '''
    mail.send(msg)
    return 'success', 200


def send_notice_email(message_content, username):
    target_email = db_get_email_by_username(username)
    msg = Message('协心力通知', sender=('协心力', 'djk20@foxmail.com'), recipients=[target_email])
    msg.body = 'body'
    msg.html = '''
        <div>亲爱的协心力用户：</div>
        <div>&nbsp;&nbsp;您好！协心力通知您，该服用药物：''' + message_content + '''了！请您尽快吃药，谢谢！</div>
        <div>&nbsp;</div>
        <div>协心力</div>
        '''
    mail.send(msg)
    return 'success', 200

    
def send_mail(app, msg):
    with app.app_context():
        mail.send(msg)
        return 'success', 200


@email_bp.route('/sendPWChangeVerifyEmail/', methods=['POST'])
@swag_from('swagger/sendPWChangeVerifyEmail.yml')
def send_pw_change_verify_email():
    body_data = request.json
    target_user = body_data['username']
    target_email = db_get_email_by_username(target_user)
    verify_code = ""
    for _ in range(0, 6):
        verify_code += str(random.randint(0, 9))
    status, res = db_add_verify_code(verify_code, target_email)
    if status is False:
        return res, 500
    msg = Message('协心力验证码', sender=('协心力', 'djk20@foxmail.com'), recipients=[target_email])
    msg.body = 'body'
    msg.html = '''
        <div>亲爱的协心力用户：</div>
        <div>&nbsp;&nbsp;您好！您的协心力验证码为''' + verify_code + '''，该验证码将在15分钟后失效，请您尽快填写，谢谢！</div>
        <div>&nbsp;</div>
        <div>协心力</div>
        '''
    mail.send(msg)
    return 'success', 200
