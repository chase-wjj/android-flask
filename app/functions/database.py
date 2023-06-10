import datetime

from app.models.models import User, Blog, Friendship, VerifyCode, Comment, ChatMessage, Checklist
from app.models.models import UserLoggedIn
from app.models.models import HealthAid
from app.models.models import FriendRequest
from app.extensions.extensions import db


# 添加新的用户
def db_add_new_user(username, password):
    try:
        now = datetime.datetime.now()
        user = User(username=username, password=password, email='', mobile='', time=now, job='', home='', edit='',
                    friend_group='default', photo='')
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 修改用户信息
def db_edit_user(username, mobile, job, home, edit, photo):
    try:
        cursor = db.session.execute(
            "SELECT mobile, job, home, edit, photo FROM user WHERE username = '" + username + "';"
        )
        for cur in cursor:
            mobile_0 = cur[0]
            job_0 = cur[1]
            home_0 = cur[2]
            edit_0 = cur[3]
            photo_0 = cur[4]
        if mobile is None:
            mobile = mobile_0
        if job is None:
            job = job_0
        if home is None:
            home = home_0
        if edit is None:
            edit = edit_0
        if photo is None:
            photo = photo_0

        db.session.execute("UPDATE user SET mobile = '" + mobile + "', job = '" + job + "', home = '" + home +
                           "', edit = '" + edit + "', photo = '" + photo + "' WHERE username = '" + username + "';")
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 修改密码
def db_change_user_password(username, new_password):
    try:
        db.session.execute("UPDATE user SET password = '" + new_password + "' WHERE username = '" + username + "';")
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


# 用户认证
def db_verify_user(username, password):
    try:
        cursor = db.session.execute("SELECT password FROM user WHERE username ='" + username + "';")
        for cur in cursor:
            pw = cur[0]
        return password == pw
    except Exception as e:
        print(e)
        return False


# search user's email from database by username
# return value: email(str)
def db_get_email_by_username(username):
    try:
        cursor = db.session.execute("SELECT email FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            return cur[0]
    except Exception as e:
        print(str(e))
        return False


def db_add_blog(username, blog_title, blog_content):
    try:
        now = datetime.datetime.now()
        current_datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
        blog = Blog(username=username, blog_title=blog_title, blog_content=blog_content,
                    time=current_datetime_str,like=0)
        db.session.add(blog)
        db.session.commit()
        return True, str(now)[:-7]
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_blog(username, blog_id):
    try:
        cursor = db.session.execute("SELECT username FROM blog WHERE id = '" + str(blog_id) + "';")
        if not cursor:
            return False, 'no such blog'
        if username != 'test':
            for cur in cursor:
                if cur[0] != username:
                    return False, 'Permission denied'
        db.session.execute("DELETE FROM blog WHERE id = '" + str(blog_id) + "';")
        db.session.execute("DELETE FROM comment WHERE blog_id = '" + str(blog_id) + "';")
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_all_blogs():
    try:
        blogs = []
        cursor = db.session.execute("SELECT * FROM blog;")
        for cur in cursor:
            blog = {'id': str(cur[0]), 'username': cur[1], 'blog_title': cur[2], 'blog_content': cur[3],
                    'time': str(cur[4]),'like': str(cur[5])}
            blogs.append(blog)
        return True, blogs
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_search_blog_by_id(blog_id):
    try:
        cursor = db.session.execute("SELECT * FROM blog WHERE id = '" + blog_id + "';")
        for cur in cursor:
            blog = {'id': str(cur[0]), 'username': cur[1], 'blog_title': cur[2], 'blog_content': cur[3],
                    'summary': cur[4], 'labels': cur[5].split(' '), 'time': str(cur[6])[:-7]}
            return True, blog
        return False, "no such blog id"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_my_all_blogs(username):
    try:
        blogs = []
        cursor = db.session.execute("SELECT * FROM blog WHERE username = '" + username + "';")
        for cur in cursor:
            blog = {'id': str(cur[0]), 'username': cur[1], 'blog_title': cur[2], 'blog_content': cur[3],
                    'time': str(cur[4]),'like': str(cur[5])}
            blogs.append(blog)
        return True, blogs
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_new_friend_request(username, friend_name, remark):
    try:
        friend_list = db_search_all_friend_by_name_no_grouped(username)
        if friend_list is False:
            return False
        if friend_name in friend_list:
            return False
        now = datetime.datetime.now()
        friend_request = FriendRequest(username_1=username, username_2=friend_name, remark=remark, time=now)
        db.session.add(friend_request)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def db_get_all_friend_request(username):
    try:
        friend_requests = []
        cursor = db.session.execute(
            "SELECT username_1, remark FROM friend_request WHERE username_2 ='" + username + "';"
        )
        for cur in cursor:
            friend_requests.append({'friend_name': cur[0], 'remark': cur[1]})
        return friend_requests
    except Exception as e:
        print(str(e))
        return False


def db_reject_friend_request(username, friend_name):
    try:
        db.session.execute(
            "DELETE FROM friend_request WHERE username_2 = '" + username + "' AND username_1 = '" + friend_name + "';"
        )
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def db_add_new_friend(username, friend_name):
    try:
        friend_list = db_search_all_friend_by_name_no_grouped(username)
        if friend_list is False:
            return False
        db.session.execute(
            "DELETE FROM friend_request WHERE username_2 = '" + username + "' AND username_1 = '" + friend_name + "';"
        )
        if friend_name in friend_list:
            return False
        now = datetime.datetime.now()
        friendship = Friendship(
            username_1=username, username_2=friend_name, group_1='default', group_2='default', time=now
        )
        db.session.add(friendship)
        db.session.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def db_search_all_friend_by_name_grouped(username):
    try:
        friends = {}
        cursor = db.session.execute("SELECT friend_group FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            groups = cur[0].split(' ')
        for group in groups:
            friends[group] = []
        user_logged_in = []
        cursor = db.session.execute("SELECT username FROM user_logged_in;")
        for cur in cursor:
            user_logged_in.append(cur[0])
        cursor = db.session.execute("SELECT username_2, group_1 FROM friendship WHERE username_1 = '" + username + "';")
        for cur in cursor:
            friends[cur[1]].append({'username': cur[0], 'status': cur[0] in user_logged_in})
        cursor = db.session.execute("SELECT username_1, group_2 FROM friendship WHERE username_2 = '" + username + "';")
        for cur in cursor:
            friends[cur[1]].append({'username': cur[0], 'status': cur[0] in user_logged_in})
        return friends   # 返回朋友list
    except Exception as e:
        print(str(e))
        return False


def db_search_all_friend_by_name_no_grouped(username):
    try:
        friends = []
        cursor = db.session.execute("SELECT username_2, group_1 FROM friendship WHERE username_1 = '" + username + "';")
        for cur in cursor:
            friends.append(cur[0])
        cursor = db.session.execute("SELECT username_1, group_2 FROM friendship WHERE username_2 = '" + username + "';")
        for cur in cursor:
            friends.append(cur[0])
        return friends   # 返回朋友list
    except Exception as e:
        print(str(e))
        return False


def db_add_new_group(username, new_group):
    try:
        cursor = db.session.execute("SELECT friend_group FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            groups = cur[0].split(' ')
        if new_group in groups:
            return False, 'already has the group'
        for group in groups:
            new_group += (' ' + group)
        db.session.execute("UPDATE user SET friend_group = '" + new_group + "' WHERE username = '" + username + "';")
        db.session.commit()
        return True, ''
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_delete_old_group(username, old_group):
    try:
        if old_group == 'default':
            return False, 'can not delete group "default"'
        cursor = db.session.execute("SELECT friend_group FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            groups = cur[0].split(' ')
        if old_group not in groups:
            return False, 'no such group'
        friends = db_search_all_friend_by_name_grouped(username)
        for friend in friends[old_group]:
            db_change_friend_group(username, friend['username'], 'default')
        groups.remove(old_group)
        new_group = ''
        for group in groups:
            new_group += (' ' + group)
        new_group = new_group[1:]
        db.session.execute("UPDATE user SET friend_group = '" + new_group + "' WHERE username = '" + username + "';")
        db.session.commit()
        return True, ''
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_change_friend_group(username, friend_name, new_group):
    try:
        cursor = db.session.execute("SELECT friend_group FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            groups = cur[0].split(' ')
        if new_group not in groups:
            return False, 'no such group'
        db.session.execute("UPDATE friendship SET group_1 = '" + new_group + "' WHERE username_1 = '" + username +
                           "' AND username_2 = '" + friend_name + "';")
        db.session.execute("UPDATE friendship SET group_2 = '" + new_group + "' WHERE username_2 = '" + username +
                           "' AND username_1 = '" + friend_name + "';")
        db.session.commit()
        return True, ''
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_delete_old_friend(username, friend_name):
    try:
        friend_list = db_search_all_friend_by_name_no_grouped(username)
        if friend_name in friend_list:
            db.session.execute("DELETE FROM friendship WHERE username_1 = '" + username + "' AND username_2 ="
                               " '" + friend_name + "';")
            db.session.execute("DELETE FROM friendship WHERE username_2 = '" + username + "' AND username_1 ="
                               " '" + friend_name + "';")
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(str(e))
        return False


def db_add_verify_code(verify_code, email):
    try:
        now = datetime.datetime.now()
        code = VerifyCode(code=verify_code, email=email, created_time=now)
        db.session.add(code)
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_check_verify_code(verify_code, email):
    try:
        now = datetime.datetime.now()
        cursor = db.session.execute("SELECT created_time FROM verify_code WHERE code ='" + verify_code + "'"
                                    " AND email = '" + email + "';")
        for cur in cursor:
            if (now - datetime.datetime.strptime(cur[0], "%Y-%m-%d %H:%M:%S.%f")).seconds <= 900:
                return True, 'success'
        return False, 'timeout'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_comment(username, blog_id, content):
    try:
        now = datetime.datetime.now()
        current_datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.session.execute("SELECT id FROM blog WHERE id = '" + str(blog_id) + "';")
        for _ in cursor:
            comment = Comment(username=username, content=content, blog_id=blog_id, time=current_datetime_str)
            db.session.add(comment)
            db.session.commit()
            return True, 'success'
        return False, 'no such blog'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_comment(username, comment_id):
    try:
        cursor = db.session.execute("SELECT username FROM comment WHERE id = '" + str(comment_id) + "';")
        if not cursor:
            return False, 'no such comment'
        if username != 'test':
            for cur in cursor:
                if cur[0] != username:
                    return False, 'Permission denied'
        db.session.execute("DELETE FROM comment WHERE id = '" + str(comment_id) + "';")
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_all_comments_by_blog_id(blog_id):
    try:
        comments = []
        cursor = db.session.execute("SELECT * FROM comment WHERE blog_id = '" + str(blog_id) + "';")
        for cur in cursor:
            comment = {'id': str(cur[0]), 'blog_id': str(cur[1]), 'username': cur[2], 'content': cur[3],
                       'time': str(cur[4])}
            comments.append(comment)
        return True, comments
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_message(username, friend_name, content):
    try:
        now = datetime.datetime.now()
        chat_message = ChatMessage(username_1=username, username_2=friend_name, content=content, time=now)
        db.session.add(chat_message)
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_message_by_username(username):
    try:
        message_list = []
        cursor = db.session.execute(
            "SELECT username_1, content, time FROM chat_message WHERE username_2 = '" + username + "';"
        )
        for cur in cursor:
            message_list.append({'sender': cur[0], 'receiver': username, 'content': cur[1], 'time': cur[2]})
        cursor = db.session.execute(
            "SELECT username_2, content, time FROM chat_message WHERE username_1 = '" + username + "';"
        )
        for cur in cursor:
            message_list.append({'sender': username, 'receiver': cur[0], 'content': cur[1], 'time': cur[2]})
        return True, message_list
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_checklist(username, checklist, remark):
    try:
        now = datetime.datetime.now()
        checklist = Checklist(username=username, checklist=checklist, remark=remark, time=now)
        db.session.add(checklist)
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_all_checklists(username):
    try:
        checklists = []
        cursor = db.session.execute(
            "SELECT checklist, remark, id FROM checklist WHERE username = '" + username + "';"
        )
        for cur in cursor:
            checklists.append({'checklist': cur[0], 'remark': cur[1], 'id': str(cur[2])})
        return True, checklists
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_checklist(username, checklist_id):
    try:
        cursor = db.session.execute(
            "SELECT id FROM checklist WHERE username = '" + username + "' AND id = '" + str(checklist_id) + "';"
        )
        for _ in cursor:
            db.session.execute("DELETE FROM checklist WHERE username = '" + username + "' AND id = '" +
                               str(checklist_id) + "';")
            db.session.commit()
            return True, 'success'
        return False, 'no such checklist'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_health_aid(username, title, abstract, diya, gaoya, xuetang, xuezhi, content):
    try:
        now = datetime.datetime.now()
        health_aid = HealthAid(username=username, title=title, abstract=abstract, diya=diya, gaoya=gaoya,
                               xuetang=xuetang, xuezhi=xuezhi, content=content, time=now)
        db.session.add(health_aid)
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_all_health_aid(username):
    try:
        health_aids = []
        cursor = db.session.execute("SELECT title, abstract, diya, gaoya, xuetang, xuezhi, content, time, id FROM "
                                    "health_aid WHERE username = '" + username + "';")
        abnormal = {}
        for cur in cursor:
            if float(cur[2]) < 60:
                abnormal['diya'] = 'too low'
            elif float(cur[2]) > 90:
                abnormal['diya'] = 'too high'
            if float(cur[3]) < 90:
                abnormal['gaoya'] = 'too low'
            elif float(cur[3]) > 140:
                abnormal['gaoya'] = 'too high'
            if float(cur[4]) < 3.9:
                abnormal['xuetang'] = 'too low'
            if float(cur[4]) > 6.0:
                abnormal['xuetang'] = 'too high'
            if float(cur[5]) < 0.45:
                abnormal['xuezhi'] = 'too low'
            if float(cur[5]) > 1.27:
                abnormal['xuezhi'] = 'too high'
            health_aids.append(
                {'title': cur[0], 'abstract': cur[1], 'diya': cur[2], 'gaoya': cur[3], 'xuetang': cur[4],
                 'xuezhi': cur[5], 'content': cur[6], 'time': str(cur[7])[:-7], 'id': str(cur[8]), 'abnormal': abnormal}
            )
        return True, health_aids
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_del_health_aid(username, health_aid_id):
    try:
        cursor = db.session.execute(
            "SELECT id FROM health_aid WHERE username = '" + username + "' AND id = '" + str(health_aid_id) + "';"
        )
        for _ in cursor:
            db.session.execute("DELETE FROM health_aid WHERE username = '" + username + "' AND id = '" +
                               str(health_aid_id) + "';")
            db.session.commit()
            return True, 'success'
        return False, 'no such health aid'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_search_user_by_name(username):
    try:
        cursor = db.session.execute("SELECT * FROM user WHERE username = '" + username + "';")
        for cur in cursor:
            user = {'id': str(cur[0]), 'username': cur[1], 'mobile': cur[4], 'job': cur[5],
                    'home': cur[6], 'edit': cur[7]}
            return True, user
        return False, "no such user"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_account_info(username):
    try:
        cursor = db.session.execute("SELECT mobile, home, job, edit, email, photo FROM user WHERE username = '" +
                                    username + "';")
        for cur in cursor:
            return True, {'email': cur[4], 'mobile': cur[0], 'home': cur[1], 'job': cur[2], 'edit': cur[3],
                          'photo': cur[5], 'username': username}
        return False, "no such user"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_set_star_blog(blog_id):
    try:
        db.session.execute("UPDATE star_blog SET blog_id = '" + str(blog_id) + "' WHERE id = '1';")
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_get_star_blog():
    try:
        cursor = db.session.execute("SELECT blog_id FROM star_blog WHERE id = '1';")
        for cur in cursor:
            if str(cur[0]) == str(0):
                return False, "no star blog"
            return True, cur[0]
        return False, "no star blog"
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_add_logged_in_user(username):
    try:
        now = datetime.datetime.now()
        exp_datetime = now + datetime.timedelta(hours=2)
        user = UserLoggedIn(username=username, time=exp_datetime)
        db.session.add(user)
        db.session.commit()
        return True, 'success'
    except Exception as e:
        print(str(e))
        return False, str(e)


def db_delete_logged_in_user(username):
    try:
        cursor = db.session.execute("SELECT id FROM user_logged_in WHERE username = '" + username + "';")
        for _ in cursor:
            db.session.execute("DELETE FROM user_logged_in WHERE username = '" + username + "';")
            db.session.commit()
            return True, 'success'
        return False, 'no such user'
    except Exception as e:
        print(str(e))
        return False, str(e)
