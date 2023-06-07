import os
import datetime

from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models.models import User, StarBlog


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

# migrate = Migrate(app, db)
# manager.add_command('db', MigrateCommand)


@manager.command
def init_test_db():
    """Init test db"""
    db.drop_all()
    db.create_all()
    test_account = User(username="test", password="d9d2633473d309c33f7f0c9ddd05e269", email="", mobile="", job="",
                        home="", edit="", time=datetime.datetime.now(), friend_group="default", photo="")
    db.session.add(test_account)
    test_account = User(username="test2", password="d9d2633473d309c33f7f0c9ddd05e269", email="", mobile="", job="",
                        home="", edit="", time=datetime.datetime.now(), friend_group="default", photo="")
    db.session.add(test_account)
    star_blog = StarBlog(blog_id=0)
    db.session.add(star_blog)
    db.session.commit()


@manager.command
def init_db():
    """Init db"""
    db.drop_all()
    db.create_all()
    star_blog = StarBlog(blog_id=0)
    db.session.add(star_blog)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
