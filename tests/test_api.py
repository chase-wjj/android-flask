# 集成测试
from flask import current_app

import unittest
import datetime
import json

from app.models.models import User, VerifyCode, StarBlog
from app import create_app, db


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = current_app.test_client()

        db.drop_all()
        db.create_all()

        test_account = User(username="test", password="test", email="", mobile="", job="",
                            home="", edit="", time=datetime.datetime.now(), friend_group="default", photo="")
        db.session.add(test_account)
        code = VerifyCode(code='123456', email='wangqj20@mails.tsinghua.edu.cn', created_time=datetime.datetime.now())
        db.session.add(code)
        code = VerifyCode(code='123456', email='djk20@mails.tsinghua.edu.cn', created_time=datetime.datetime.now())
        db.session.add(code)
        star_blog = StarBlog(blog_id=0)
        db.session.add(star_blog)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    def test_account_and_chat(self):
        """
        id="41"
        """
        data = {
            'username': 'test2',
            'password': 'test2',
            'email': 'wangqj20@mails.tsinghua.edu.cn',
            'verify_code': '123456'
        }
        # test2账号注册登录
        response = self.client.post('/account/register/', json=data)
        self.assertEqual(201, response.status_code)
        self.assertTrue('success' in response.data.decode(), "")

        response = self.client.get('/account/isLoggedIn/')
        self.assertEqual(401, response.status_code)
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt_2 = json_data['jwt']
        response = self.client.get('/account/isLoggedIn/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)

        # test2对test发出好友请求
        response = self.client.get('/account/searchUser/test/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual('test', json_data['username'])
        response = self.client.post('/account/sendAddFriendRequest/',
                                    headers={'Authorization': jwt_2},
                                    json={'friend_name': 'test', 'remark': ''}
                                    )
        self.assertEqual(201, response.status_code)

        # test查看并拒绝test2的好友请求
        test_account_data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=test_account_data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']
        response = self.client.get('/account/getFriendRequests/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([{'friend_name': 'test2', 'remark': ''}], json_data['friendRequestList'])
        response = self.client.post('/account/handleFriendRequest/',
                                    headers={'Authorization': jwt},
                                    json={'friend_name': 'test2', 'type': '1'}
                                    )
        self.assertEqual(200, response.status_code)

        # test2账号再次对test账号发出好友请求，test同意好友请求，并双方验证是否都成功添加
        response = self.client.post('/account/sendAddFriendRequest/',
                                    headers={'Authorization': jwt_2},
                                    json={'friend_name': 'test', 'remark': ''}
                                    )
        self.assertEqual(201, response.status_code)
        response = self.client.post('/account/handleFriendRequest/',
                                    headers={'Authorization': jwt},
                                    json={'friend_name': 'test2', 'type': '2'}
                                    )
        self.assertEqual(201, response.status_code)
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual({'default': [{'username': 'test2', 'status': True}]}, json_data['friendList'])
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual({'default': [{'username': 'test', 'status': True}]}, json_data['friendList'])

        # test2账号在已经加了test为好友的情况下再次对test账号发送好友请求，预期失败
        response = self.client.post('/account/sendAddFriendRequest/',
                                    headers={'Authorization': jwt_2},
                                    json={'friend_name': 'test', 'remark': ''}
                                    )
        self.assertEqual(500, response.status_code)

        # test账号对test2账号进行分组管理，首先创建一个新组TEST，再将其移到该组，然后再删除TEST组，此时test2账号应该被自动移动回default组
        response = self.client.post('/account/addGroup/', headers={'Authorization': jwt}, json={'group_name': 'TEST'})
        self.assertEqual(201, response.status_code)
        response = self.client.post('/account/changeGroupOfFriend/',
                                    headers={'Authorization': jwt},
                                    json={'friend_name': 'test2', 'group_name': 'TEST'}
                                    )
        self.assertEqual(201, response.status_code)
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual({'default': [], 'TEST': [{'username': 'test2', 'status': True}]}, json_data['friendList'])
        response = self.client.post('/account/deleteGroup/',
                                    headers={'Authorization': jwt},
                                    json={'group_name': 'TEST'}
                                    )
        self.assertEqual(200, response.status_code)
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        self.assertEqual({'default': [{'username': 'test2', 'status': True}]}, json.loads(response.data)['friendList'])

        # 进行不允许的分组管理操作：删除default组；删除不存在的TEST组，添加重复组default
        response = self.client.post('/account/deleteGroup/',
                                    headers={'Authorization': jwt},
                                    json={'group_name': 'default'}
                                    )
        self.assertEqual(500, response.status_code)
        response = self.client.post('/account/deleteGroup/',
                                    headers={'Authorization': jwt},
                                    json={'group_name': 'TEST'}
                                    )
        self.assertEqual(500, response.status_code)
        response = self.client.post('/account/addGroup/',
                                    headers={'Authorization': jwt},
                                    json={'group_name': 'default'}
                                    )
        self.assertEqual(500, response.status_code)

        # 正式发送消息
        chat_data = {'friend_name': 'test', 'content': 'TEST_CONTENT'}
        response = self.client.post('/chat/sendMessage/', headers={'Authorization': jwt_2}, json=chat_data)
        self.assertEqual(201, response.status_code)

        # 双方查看消息
        response = self.client.get('/chat/getMessage/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        chat_data_response = json_data['message_list'][0]
        self.assertEqual('test2', chat_data_response['sender'])
        self.assertEqual('test', chat_data_response['receiver'])
        self.assertEqual('TEST_CONTENT', chat_data_response['content'])
        response = self.client.get('/chat/getMessage/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)
        chat_data_response = json.loads(response.data)['message_list'][0]
        self.assertEqual('test2', chat_data_response['sender'])
        self.assertEqual('test', chat_data_response['receiver'])
        self.assertEqual('TEST_CONTENT', chat_data_response['content'])

        # 最后删除好友，并检测是否删除成功
        response = self.client.post('/account/deleteFriend/',
                                    headers={'Authorization': jwt},
                                    json={'friend_name': 'test2'}
                                    )
        self.assertEqual(200, response.status_code)
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual({'default': []}, json_data['friendList'])
        response = self.client.get('/account/getFriends/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual({'default': []}, json_data['friendList'])

        # 获取并修改账号信息
        response = self.client.get('/account/getAccountInfo/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual(
            {'email': '', 'mobile': '', 'home': '', 'job': '', 'edit': '', 'photo': '', 'username': 'test'},
            json_data
        )
        response = self.client.post('/account/changeAccountInfo/', headers={'Authorization': jwt}, json={'job': 'code'})
        self.assertEqual(201, response.status_code)
        response = self.client.get('/account/getAccountInfo/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual(
            {'email': '', 'mobile': '', 'home': '', 'job': 'code', 'edit': '', 'photo': '', 'username': 'test'},
            json_data
        )

        # 改密码并退出重登
        response = self.client.post('/account/changePassword/',
                                    json={'username': 'test2', 'new_password': 'TEST2', 'verify_code': '123456'}
                                    )
        self.assertEqual(201, response.status_code)
        response = self.client.get('/account/logout/', headers={'Authorization': jwt_2})
        self.assertEqual(401, response.status_code)
        response = self.client.post('/account/login/', json={'username': 'test2', 'password': 'TEST2'})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt_2 = json_data['jwt']
        response = self.client.get('/account/isLoggedIn/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)

    def test_email(self):
        """
        id=""
        """
        # 测试发送注册邮件
        data = {'email': 'djk20@mails.tsinghua.edu.cn'}
        response = self.client.post('/email/sendVerifyEmail/', json=data)
        self.assertEqual(200, response.status_code)

        # 测试发送重置密码邮件（先注册一个test3账号）
        data = {
            'username': 'test3',
            'password': 'test3',
            'email': 'djk20@mails.tsinghua.edu.cn',
            'verify_code': '123456'
        }
        response = self.client.post('/account/register/', json=data)
        self.assertEqual(201, response.status_code)
        self.assertTrue('success' in response.data.decode(), "")
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        response = self.client.post('/email/sendPWChangeVerifyEmail/', json=data)
        self.assertEqual(200, response.status_code)

    def test_schedule(self):
        """
        id=""
        """
        data = {
            'username': 'test2',
            'password': 'test2',
            'email': 'wangqj20@mails.tsinghua.edu.cn',
            'verify_code': '123456'
        }
        self.client.post('/account/register/', json=data)
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        jwt_2 = json.loads(response.data)['jwt']

        # 添加并删除服药提醒
        data = {'schedule_time': '13:40:00', 'schedule_message': 'test'}
        response = self.client.post(
            '/timer/addTimer/',
            json=data,
            headers={'Authorization': jwt_2}
        )
        self.assertEqual(201, response.status_code)
        response = self.client.post('/timer/deleteTimer/', headers={'Authorization': jwt_2})
        self.assertEqual(200, response.status_code)

    def test_blog(self):
        """
        id=""
        """
        # 登录并查看帖子，确认帖子列表为空，再发帖子
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']

        response = self.client.get('/blog/getBlogs/', headers={'Authorization': jwt})
        response_json = json.loads(response.data)
        blogs = response_json['blogList']
        self.assertEqual([], blogs)

        data = {
            'blog_title': 'TEST_TITLE',
            'blog_content': 'TEST_CONTENT',
            'summary': 'TEST_SUMMARY',
            'labels': 'label1 label2'
        }
        response = self.client.post('/blog/publishBlog/', json=data, headers={'Authorization': jwt})
        self.assertEqual(201, response.status_code)

        # 通过三个API：by ID、by username、by *获取刚发的帖子
        response = self.client.get('/blog/getMyBlogs/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        blogs = response_json['blogList']
        for blog in blogs:
            self.assertEqual('test', blog['username'])
            self.assertEqual('TEST_TITLE', blog['blog_title'])
            self.assertEqual('TEST_CONTENT', blog['blog_content'])
            self.assertEqual('TEST_SUMMARY', blog['summary'])
            self.assertEqual(['label1', 'label2'], blog['labels'])

        response = self.client.get('/blog/getBlogs/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        blogs = response_json['blogList']
        for blog in blogs:
            self.assertEqual('test', blog['username'])
            self.assertEqual('TEST_CONTENT', blog['blog_content'])
            self.assertEqual('TEST_TITLE', blog['blog_title'])
            self.assertEqual('TEST_SUMMARY', blog['summary'])
            self.assertEqual(['label1', 'label2'], blog['labels'])
            blog_id = blog['id']

        response = self.client.get('/blog/getBlogByID/' + str(blog_id) + '/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual('TEST_CONTENT', response_json['blog_content'])
        self.assertEqual('test', response_json['username'])
        self.assertEqual('TEST_TITLE', response_json['blog_title'])
        self.assertEqual('TEST_SUMMARY', response_json['summary'])
        self.assertEqual(['label1', 'label2'], response_json['labels'])

        # 发布并查看评论
        response = self.client.get('/blog/getComments/' + str(blog_id) + '/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        comments = response_json['commentList']
        self.assertEqual([], comments)

        data = {'blog_id': blog_id, 'content': 'TEST_COMMENT'}
        response = self.client.post('/blog/publishComment/', json=data, headers={'Authorization': jwt})
        self.assertEqual(201, response.status_code)
        data = {'blog_id': blog_id, 'content': 'TEST_COMMENT'}
        self.client.post('/blog/publishComment/', json=data, headers={'Authorization': jwt})

        response = self.client.get('/blog/getComments/' + str(blog_id) + '/', headers={'Authorization': jwt})
        response_json = json.loads(response.data)
        comments = response_json['commentList']
        comment_ids = []
        for comment in comments:
            self.assertEqual(blog_id, str(comment['blog_id']))
            self.assertEqual('test', comment['username'])
            self.assertEqual('TEST_COMMENT', comment['content'])
            comment_ids.append(comment['id'])

        # 删除评论及帖子
        data['comment_id'] = comment_ids[0]
        response = self.client.post('/blog/deleteComment/', json=data, headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)

        data = {'blog_id': blog_id}
        response = self.client.post('/blog/deleteBlog/', json=data, headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response = self.client.get('/blog/getBlogs/', headers={'Authorization': jwt})
        response_json = json.loads(response.data)
        blogs = response_json['blogList']
        self.assertEqual([], blogs)
        response = self.client.get('/blog/getComments/' + str(blog_id) + '/', headers={'Authorization': jwt})
        response_json = json.loads(response.data)
        comments = response_json['commentList']
        self.assertEqual([], comments)

    def test_test_account(self):
        """
        id=""
        """
        # 测试管理员账号
        # 首先注册一个非管理员账号发帖、发评
        data = {
            'username': 'test3',
            'password': 'test3',
            'email': 'djk20@mails.tsinghua.edu.cn',
            'verify_code': '123456'
        }
        response = self.client.post('/account/register/', json=data)
        self.assertEqual(201, response.status_code)
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt_3 = json_data['jwt']

        data = {
            'blog_title': 'TEST_TITLE',
            'blog_content': 'TEST_CONTENT?',
            'summary': 'TEST_SUMMARY',
            'labels': 'label1 label2'
        }
        response = self.client.get('/blog/getBlogs/', headers={'Authorization': jwt_3})
        blogs = json.loads(response.data)['blogList']
        self.assertEqual([], blogs)
        response = self.client.post('/blog/publishBlog/', json=data, headers={'Authorization': jwt_3})
        self.assertEqual(201, response.status_code)
        data = {'blog_id': '1', 'content': 'TEST_COMMENT'}
        response = self.client.post('/blog/publishComment/', json=data, headers={'Authorization': jwt_3})
        self.assertEqual(201, response.status_code)

        # 登录管理员账号
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']

        # 设置并获取加精帖子
        response = self.client.get('/blog/getStarBlog/', headers={'Authorization': jwt})
        self.assertEqual(500, response.status_code)
        response = self.client.post('/blog/setStarBlog/', headers={'Authorization': jwt}, json={'blog_id': 1})
        self.assertEqual(201, response.status_code)
        response = self.client.get('/blog/getStarBlog/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        self.assertEqual('1', str(json.loads(response.data)['id']))

        # 管理员账号任意删帖删评，并确认删除成功
        response = self.client.post('/blog/deleteComment/', json={'comment_id': '1'}, headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response = self.client.get('/blog/getComments/1/', headers={'Authorization': jwt})
        response_json = json.loads(response.data)
        comments = response_json['commentList']
        self.assertEqual([], comments)
        data = {'blog_id': 1}
        response = self.client.post('/blog/deleteBlog/', json=data, headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        response = self.client.get('/blog/getBlogs/', headers={'Authorization': jwt})
        blogs = json.loads(response.data)['blogList']
        self.assertEqual([], blogs)

    def test_checklist(self):
        """
        id=""
        """
        # 登录并查看检查单，确认检查单列表为空，再上传检查单
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']

        response = self.client.get('/checklist/getChecklist/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([], json_data['checklist'])
        response = self.client.post('/checklist/uploadChecklist/',
                                    headers={'Authorization': jwt},
                                    json={'checklist': 's'}
                                    )
        self.assertEqual(201, response.status_code)
        response = self.client.get('/checklist/getChecklist/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([{'checklist': 's', 'remark': '', 'id': '1'}], json_data['checklist'])

        # 删除检查单，并确认删除成功
        response = self.client.post('/checklist/deleteChecklist/',
                                    headers={'Authorization': jwt},
                                    json={'checklist_id': '1'}
                                    )
        self.assertEqual(200, response.status_code)
        response = self.client.get('/checklist/getChecklist/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([], json_data['checklist'])

    def test_health_aid(self):
        """
        id=""
        """
        # 登录并查看健康日志，确认健康日志列表为空，再上传健康日志
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']

        response = self.client.get('/healthAid/getHealthAid/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([], json_data['health_aid'])
        response = self.client.post(
            '/healthAid/uploadHealthAid/',
            headers={'Authorization': jwt},
            json={
                'title': 'TEST_HEALTH_AID',
                'abstract': 'TEST_ABSTRACT',
                'diya': '80',
                'gaoya': '120',
                'xuetang': '8.0',
                'xuezhi': '1.00',
                'content': 'TEST_CONTENT'
            }
        )
        self.assertEqual(201, response.status_code)
        response = self.client.get('/healthAid/getHealthAid/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual('TEST_HEALTH_AID', json_data['health_aid'][0]['title'])
        self.assertEqual('TEST_ABSTRACT', json_data['health_aid'][0]['abstract'])
        self.assertEqual('80', json_data['health_aid'][0]['diya'])
        self.assertEqual('120', json_data['health_aid'][0]['gaoya'])
        self.assertEqual('8.0', json_data['health_aid'][0]['xuetang'])
        self.assertEqual('1.00', json_data['health_aid'][0]['xuezhi'])
        self.assertEqual('TEST_CONTENT', json_data['health_aid'][0]['content'])
        self.assertEqual('1', json_data['health_aid'][0]['id'])
        self.assertEqual({'xuetang': 'too high'}, json_data['health_aid'][0]['abnormal'])

        # 删除检查单，并确认删除成功
        response = self.client.post('/healthAid/deleteHealthAid/',
                                    headers={'Authorization': jwt},
                                    json={'health_aid_id': '1'}
                                    )
        self.assertEqual(200, response.status_code)
        response = self.client.get('/healthAid/getHealthAid/', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        self.assertEqual([], json_data['health_aid'])

    @unittest.skip("该功能由于1月初百度百科突然上线的反爬机制而无法使用，因此跳过测试")
    def test_search_api(self):
        """
        id=""
        """
        # 登录并依次搜索不存在的、存在的词条
        data = {'username': 'test', 'password': 'test'}
        response = self.client.post('/account/login/', json=data)
        self.assertEqual(200, response.status_code)
        json_data = json.loads(response.data)
        jwt = json_data['jwt']
        response = self.client.get('/search/searchByWord/?search_word=djk', headers={'Authorization': jwt})
        self.assertEqual(500, response.status_code)
        response = self.client.get('/search/searchByWord/?search_word=氯雷他定', headers={'Authorization': jwt})
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()
