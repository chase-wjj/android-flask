from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.functions.database import db_del_blog, db_add_comment, db_del_comment, db_get_all_blogs, db_get_my_all_blogs
from app.functions.database import db_get_all_comments_by_blog_id, db_search_blog_by_id, db_set_star_blog, db_add_blog
from app.functions.database import db_get_star_blog
from app.functions.account import login_required, identify

blog_bp = Blueprint("blog", __name__)


# 发表博客
@blog_bp.route("/publishBlog/", methods=['POST'])
@swag_from('swagger/publishBlog.yml')
def publish_blog():
    body_data = request.json
    username = body_data['username']
    blog_title = body_data['blog_title']
    blog_content = body_data['blog_content']
    labels = body_data['labels']
    status, message = db_add_blog(username, blog_title, blog_content,  labels)
    if status:
        return jsonify({'time': message}), 201
    else:
        return jsonify({'errorInfo': message}), 500


@blog_bp.route("/deleteBlog/", methods=['POST'])
@login_required
@swag_from('swagger/deleteBlog.yml')
def delete_blog():
    body_data = request.json
    username = body_data['username']
    blog_id = body_data['blog_id']
    status, message = db_del_blog(username, blog_id)
    if status:
        return message, 200
    else:
        return message, 500


@blog_bp.route("/getBlogs/", methods=['GET'])
@swag_from('swagger/getBlogs.yml')
def get_blogs():
    status, blogs = db_get_all_blogs()
    if status:
        return jsonify({'blogList': blogs}), 200
    else:
        return status, 500


@blog_bp.route("/getBlogByID/<blog_id>/", methods=['GET'])
@login_required
@swag_from('swagger/getBlogById.yml')
def get_blog_by_id(blog_id):
    status, blog = db_search_blog_by_id(blog_id)
    if status:
        return jsonify(blog), 200
    else:
        return status, 500


@blog_bp.route("/getMyBlogs/", methods=['GET'])
@login_required
@swag_from('swagger/getMyBlogs.yml')
def get_my_blogs():
    username = body_data['username']
    status, blogs = db_get_my_all_blogs(username)
    if status:
        return jsonify({'blogList': blogs}), 200
    else:
        return status, 500


@blog_bp.route("/publishComment/", methods=['POST'])
@login_required
@swag_from('swagger/publishComment.yml')
def publish_comment():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    blog_id = body_data['blog_id']
    content = body_data['content']
    status, message = db_add_comment(username, blog_id, content)
    if status:
        return message, 201
    else:
        return message, 500


@blog_bp.route("/deleteComment/", methods=['POST'])
@login_required
@swag_from('swagger/deleteComment.yml')
def delete_comment():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    comment_id = body_data['comment_id']
    status, message = db_del_comment(username, comment_id)
    if status:
        return message, 200
    else:
        return message, 500


@blog_bp.route("/getComments/<blog_id>/", methods=['GET'])
@login_required
@swag_from('swagger/getComments.yml')
def get_comments(blog_id):
    status, comments = db_get_all_comments_by_blog_id(blog_id)
    if status:
        return jsonify({'commentList': comments}), 200
    else:
        return comments, 500


@blog_bp.route("/getStarBlog/", methods=['GET'])
@login_required
@swag_from('swagger/getStarBlog.yml')
def get_star_blog():
    status, result = db_get_star_blog()
    if status:
        return jsonify({'id': result}), 200
    else:
        return result, 500


@blog_bp.route("/setStarBlog/", methods=['POST'])
@login_required
@swag_from('swagger/setStarBlog.yml')
def set_star_blog():
    body_data = request.json
    username = identify(request.headers.get("Authorization", default=None))
    if username != 'test':
        return "Permission denied", 401
    blog_id = body_data['blog_id']
    status, message = db_set_star_blog(blog_id)
    if status:
        return message, 201
    else:
        return message, 500
