# 单元测试
import unittest

from app import create_app, db
from app.functions.database import db_add_new_user, db_verify_user, db_add_new_friend, db_delete_old_friend
from app.functions.database import db_search_all_friend_by_name_no_grouped


class TestBasic(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    def test_database(self):
        """
        id="40"
        """
        # 测试注册账号、验证账号等功能
        self.assertEqual(False, db_verify_user('test', 'test'))
        self.assertEqual(True, db_add_new_user('test', 'test', ''))
        self.assertEqual(True, db_verify_user('test', 'test'))
        self.assertEqual(False, db_verify_user('test', 'lalala'))

        # 测试好友功能
        self.assertEqual(True, db_add_new_user('test2', 'test2', ''))
        self.assertEqual([], db_search_all_friend_by_name_no_grouped('test'))
        self.assertEqual([], db_search_all_friend_by_name_no_grouped('test2'))

        self.assertEqual(False, db_delete_old_friend('test', 'test2'))
        self.assertEqual(False, db_delete_old_friend('test2', 'test'))

        self.assertEqual(True, db_add_new_friend('test', 'test2'))
        self.assertEqual(['test'], db_search_all_friend_by_name_no_grouped('test2'))
        self.assertEqual(['test2'], db_search_all_friend_by_name_no_grouped('test'))

        self.assertEqual(False, db_add_new_friend('test2', 'test'))
        self.assertEqual(True, db_delete_old_friend('test', 'test2'))
        self.assertEqual([], db_search_all_friend_by_name_no_grouped('test'))
        self.assertEqual([], db_search_all_friend_by_name_no_grouped('test2'))


if __name__ == '__main__':
    unittest.main()
