from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import db_add_health_aid, db_del_health_aid, db_get_all_health_aid
from app.functions.account import login_required, identify

health_aid_bp = Blueprint("healthAid", __name__)


@health_aid_bp.route('/uploadHealthAid/', methods=['POST'])
@swag_from('swagger/uploadHealthAid.yml')
@login_required
def upload_health_aid():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    title = body_data['title']
    abstract = body_data['abstract']
    diya = body_data['diya']
    gaoya = body_data['gaoya']
    xuetang = body_data['xuetang']
    xuezhi = body_data['xuezhi']
    content = body_data['content']
    status, message = db_add_health_aid(username, title, abstract, diya, gaoya, xuetang, xuezhi, content)
    if status:
        return 'success', 201
    return 'failed', 500


@health_aid_bp.route('/getHealthAid/', methods=['GET'])
@swag_from('swagger/getHealthAid.yml')
@login_required
def get_health_aid():
    username = identify(request.headers.get("Authorization", default=None))
    status, message = db_get_all_health_aid(username)
    if status:
        return jsonify({'health_aid': message}), 200
    return 'failed', 500


@health_aid_bp.route('/deleteHealthAid/', methods=['POST'])
@swag_from('swagger/deleteHealthAid.yml')
@login_required
def delete_health_aid():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    health_aid_id = body_data['health_aid_id']
    status, message = db_del_health_aid(username, health_aid_id)
    if status:
        return 'success', 200
    return 'failed', 500
