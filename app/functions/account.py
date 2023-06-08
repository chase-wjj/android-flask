import datetime

import jwt
from flask import Blueprint, request, jsonify
from functools import wraps
from flasgger import swag_from

from app.functions.database import db_add_new_user, db_edit_user, db_change_user_password, db_reject_friend_request
from app.functions.database import db_search_all_friend_by_name_grouped, db_get_email_by_username, db_add_new_friend
from app.functions.database import db_delete_old_friend, db_check_verify_code, db_add_new_friend_request, db_verify_user
from app.functions.database import db_change_friend_group, db_add_new_group, db_delete_old_group, db_get_account_info
from app.functions.database import db_add_logged_in_user, db_delete_logged_in_user, db_search_user_by_name
from app.functions.database import db_get_all_friend_request

account_bp = Blueprint("account", __name__)

key = "123456"  # TODO:将secret私钥通过配置文件导入


def generate_access_token(username: str = "", algorithm: str = 'HS256', exp: float = 2):
    """
    生成access_token
    :param username: 用户名(自定义部分)
    :param algorithm: 加密算法
    :param exp: 过期时间
    :return:token
    """

    now = datetime.datetime.utcnow()
    exp_datetime = now + datetime.timedelta(hours=exp)
    access_payload = {
        'exp': exp_datetime,
        'flag': 0,   # 标识是否为一次性token，0是，1不是
        'iat': now,   # 开始时间
        'iss': 'leon',   # 签名
        'username': username   # 用户名(自定义部分)
    }
    access_token = jwt.encode(access_payload, key, algorithm=algorithm)
    return access_token.decode()


def decode_auth_token(token: str):
    """
    解密token
    :param token:token字符串
    :return:
    """
    try:
        payload = jwt.decode(token, key=key, algorithms='HS256')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
        return ""
    else:
        return payload


def identify(auth_header: str):
    """
    用户鉴权
    """
    if auth_header:
        payload = decode_auth_token(auth_header)
        if not payload:
            return False
        if "username" in payload and "flag" in payload:
            if payload["flag"] == 0:
                return payload["username"]
            else:
                return False
    return False


def login_required(f):
    """
    登录保护，验证用户是否登录
    :param f:
    :return:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", default=None)
        if not token:
            return 'not Login', 401
        username = identify(token)
        if not username:
            return 'not Login', 401      # return 响应体, 状态码, 响应头
        return f(*args, **kwargs)
    return wrapper


@account_bp.route('/isLoggedIn/', methods=['GET'])
@swag_from('swagger/isLoggedIn.yml')
@login_required
def is_logged_in():
    return identify(request.headers.get("Authorization", default=None)), 200  # 成功通过login_required认证则返回username


@account_bp.route("/register/", methods=['POST'])
@swag_from('swagger/register.yml')
def create_new_account():
    # 注册新的账号，成功则返回 'success' 及201，否则打印错误信息到后端控制台并返回给前端
    body_data = request.json
    username = body_data['username']
    password = body_data['password']
    '''
    email = body_data['email']
    verify_code = body_data['verify_code']
    status, message = db_check_verify_code(verify_code, email)
    if status is False:
        return message, 500
        '''
    if db_add_new_user(username, password):
        return 'success', 201
    return 'failed', 500


@account_bp.route("/getAccountInfo/", methods=['POST'])
@swag_from('swagger/getAccountInfo.yml')
def get_account_info():
    body_data = request.json
    username = body_data['username']
    status, result = db_get_account_info(username)
    if status:
        return jsonify(result), 200
    return result, 500


@account_bp.route("/changeAccountInfo/", methods=['POST'])
@swag_from('swagger/changeAccountInfo.yml')
def change_account_info():
    # 修改账号信息，成功则返回 'success' 及201，否则打印错误信息到后端控制台并返回给前端
    body_data = request.json
    username = body_data['username']

    if 'mobile' in body_data and body_data['mobile'] != '':
        mobile = body_data['mobile']
    else:
        mobile = None
    if 'job' in body_data and body_data['job'] != '':
        job = body_data['job']
    else:
        job = None
    if 'home' in body_data and body_data['home'] != '':
        home = body_data['home']
    else:
        home = None
    if 'edit' in body_data and body_data['edit'] != '':
        edit = body_data['edit']
    else:
        edit = None
    if 'photo' in body_data and body_data['photo'] != '':
        photo = body_data['photo']
    else:
        photo = None

    if db_edit_user(username, mobile, job, home, edit, photo):
        return 'success', 201
    return 'failed', 500


@account_bp.route("/changePassword/", methods=['POST'])
@swag_from('swagger/changePassword.yml')
def change_password():
    # 修改密码，成功则返回 'success' 及201，否则打印错误信息到后端控制台并返回给前端
    body_data = request.json
    username = body_data['username']
    new_password = body_data['new_password']
    verify_code = body_data['verify_code']

    status, message = db_check_verify_code(verify_code, db_get_email_by_username(username))
    if status is False:
        return message, 500
    if db_change_user_password(username, new_password):
        return 'success', 201
    return 'failed', 500


@account_bp.route("/login/", methods=['POST'])
@swag_from('swagger/login.yml')
def login():
    # 登录，成功则返回200，否则返回401
    body_data = request.json
    username = body_data['username']
    password = body_data['password']
    if db_verify_user(username, password):
        status, message = db_add_logged_in_user(username)
        if not status:
            return message, 500
        return "success", 200
    return 'failed', 401


@account_bp.route('/logout/', methods=['GET'])
@swag_from('swagger/logout.yml')
@login_required
def logout():
    status, message = db_delete_logged_in_user(identify(request.headers.get("Authorization", default=None)))
    if not status:
        return message, 500
    return 'success', 401  # 直接将401发给前端，让前端收到后自动清除jwt信息


@account_bp.route("/searchUser/<username>/", methods=['GET'])
@swag_from('swagger/searchUser.yml')
@login_required
def search_user(username):
    status, result = db_search_user_by_name(username)
    if status:
        return jsonify(result), 200
    return result, 500


@account_bp.route("/sendAddFriendRequest/", methods=['POST'])
@swag_from('swagger/sendAddFriendRequest.yml')
@login_required
def send_add_friend_request():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    friend_name = body_data['friend_name']
    remark = body_data['remark']
    if db_add_new_friend_request(username, friend_name, remark):
        return 'success', 201
    return 'failed', 500


@account_bp.route("/getFriendRequests/", methods=['GET'])
@swag_from('swagger/getFriendRequests.yml')
@login_required
def get_friend_requests():
    username = identify(request.headers.get("Authorization", default=None))
    friend_request_list = db_get_all_friend_request(username)
    if friend_request_list is False:
        return 'failed', 500
    return jsonify({'friendRequestList': friend_request_list}), 200


@account_bp.route("/handleFriendRequest/", methods=['POST'])
@swag_from('swagger/handleFriendRequest.yml')
@login_required
def handle_friend_request():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    friend_name = body_data['friend_name']
    friend_request_list = db_get_all_friend_request(username)
    for friend_request in friend_request_list:
        if friend_request['friend_name'] == friend_name:
            if str(body_data['type']) == str(2):
                if db_add_new_friend(username, friend_name):
                    return 'success', 201
            elif str(body_data['type']) == str(1):
                if db_reject_friend_request(username, friend_name):
                    return 'success', 200
    return 'failed', 500


@account_bp.route("/deleteFriend/", methods=['POST'])
@swag_from('swagger/deleteFriend.yml')
@login_required
def delete_friend():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    friend_name = body_data['friend_name']
    if db_delete_old_friend(username, friend_name):
        return 'success', 200
    return 'failed', 500


@account_bp.route("/getFriends/", methods=['GET'])
@swag_from('swagger/getFriends.yml')
@login_required
def get_friends():
    username = identify(request.headers.get("Authorization", default=None))
    friend_list = db_search_all_friend_by_name_grouped(username)
    if friend_list is False:
        return 'failed', 500
    return jsonify({'friendList': friend_list}), 200


@account_bp.route("/addGroup/", methods=['POST'])
@swag_from('swagger/addGroup.yml')
@login_required
def add_group():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    group_name = str(body_data['group_name'])
    status, message = db_add_new_group(username, group_name)
    if status:
        return 'success', 201
    return message, 500


@account_bp.route("/deleteGroup/", methods=['POST'])
@swag_from('swagger/deleteGroup.yml')
@login_required
def delete_group():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    group_name = str(body_data['group_name'])
    status, message = db_delete_old_group(username, group_name)
    if status:
        return 'success', 200
    return message, 500


@account_bp.route("/changeGroupOfFriend/", methods=['POST'])
@swag_from('swagger/changeGroupOfFriend.yml')
@login_required
def change_group_of_friend():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    friend_name = body_data['friend_name']
    group_name = str(body_data['group_name'])
    status, message = db_change_friend_group(username, friend_name, group_name)
    if status:
        return 'success', 201
    return message, 500
