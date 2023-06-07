from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.extensions.search import search
from app.functions.account import login_required, identify

search_bp = Blueprint("search", __name__)


@search_bp.route("/searchByWord/", methods=["GET"])
@login_required
@swag_from("swagger/searchByWord.yml")
def search_by_word():
    body_data = request.args.to_dict()
    username = identify(request.headers.get("Authorization", default=None))
    # TODO: add search history
    search_word = body_data['search_word']
    status, message = search(search_word)
    if status:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 500
