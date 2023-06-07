from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.account import login_required, identify
from app.functions.database import db_add_checklist, db_get_all_checklists, db_del_checklist

checklist_bp = Blueprint("checklist", __name__)


@checklist_bp.route('/uploadChecklist/', methods=['POST'])
@swag_from('swagger/uploadChecklist.yml')
@login_required
def upload_checklist():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    if 'checklist' in body_data and body_data['checklist'] != '':
        checklist = body_data['checklist']
    else:
        return 'failed', 500
    if 'remark' in body_data and body_data['remark'] != '':
        remark = body_data['remark']
    else:
        remark = ''
    status, message = db_add_checklist(username, checklist, remark)
    if status:
        return 'success', 201
    return 'failed', 500


@checklist_bp.route('/getChecklist/', methods=['GET'])
@swag_from('swagger/getChecklist.yml')
@login_required
def get_checklist():
    username = identify(request.headers.get("Authorization", default=None))
    status, message = db_get_all_checklists(username)
    if status:
        return jsonify({'checklist': message}), 200
    return 'failed', 500


@checklist_bp.route('/deleteChecklist/', methods=['POST'])
@swag_from('swagger/deleteChecklist.yml')
@login_required
def delete_checklist():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    checklist_id = body_data['checklist_id']
    status, message = db_del_checklist(username, checklist_id)
    if status:
        return 'success', 200
    return 'failed', 500
