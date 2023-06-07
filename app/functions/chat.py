from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import db_add_message, db_get_message_by_username
from app.functions.account import login_required, identify

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/sendMessage/', methods=['POST'])
@swag_from('swagger/sendMessage.yml')
@login_required
def send_message():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    friend_name = body_data['friend_name']
    content = body_data['content']
    status, message = db_add_message(username, friend_name, content)
    if status:
        return message, 201
    else:
        return message, 500


@chat_bp.route('/getMessage/', methods=['GET'])
@swag_from('swagger/getMessage.yml')
@login_required
def get_message():
    username = identify(request.headers.get("Authorization", default=None))
    status, message = db_get_message_by_username(username)
    if status:
        return jsonify({'message_list': message}), 200
    else:
        return message, 500
