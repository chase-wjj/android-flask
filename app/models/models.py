from app.extensions.extensions import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="用户id")

    username = db.Column(db.String(32), unique=True, doc="账号")
    password = db.Column(db.String(256), doc="密码")
    email = db.Column(db.String(50), doc="邮箱")
    mobile = db.Column(db.String(20), doc="手机号")
    job = db.Column(db.String(50), doc="工作")
    home = db.Column(db.String(50), doc="家庭")
    edit = db.Column(db.String(50), doc="个性签名")

    time = db.Column(db.DateTime, doc="创建时间")
    friend_group = db.Column(db.String(200), doc="好友分组")
    photo = db.Column(db.String(400000), doc="头像")


class Friendship(db.Model):
    __tablename__ = 'friendship'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="关系id")
    
    username_1 = db.Column(db.String(32), doc="用户1")
    username_2 = db.Column(db.String(32), doc="用户2")

    group_1 = db.Column(db.String(20), doc="user2在user1的分组")
    group_2 = db.Column(db.String(20), doc="user1在user2的分组")

    time = db.Column(db.DateTime, doc="创建时间")


class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="博客id")
    
    username = db.Column(db.String(32), doc="账号")
    blog_title = db.Column(db.String(200), doc="blog_title")
    blog_content = db.Column(db.String(20000), doc="blog_content")  # 暂时只支持最多10000字的文章
    labels = db.Column(db.String(40), doc="labels")  # 20字标签
    time = db.Column(db.DateTime, doc="创建时间")


class VerifyCode(db.Model):
    __tablename__ = 'verify_code'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="code_id")
    code = db.Column(db.String(7), doc="code")
    email = db.Column(db.String(50), doc="邮箱")
    created_time = db.Column(db.DateTime, doc="创建时间")


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="comment_id")
    blog_id = db.Column(db.Integer, doc="blog_id")
    username = db.Column(db.String(32), doc="账号")
    content = db.Column(db.String(200), doc="content")

    time = db.Column(db.DateTime, doc="创建时间")


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="comment_id")
    username_1 = db.Column(db.String(32), doc="sender")
    username_2 = db.Column(db.String(32), doc="receiver")
    content = db.Column(db.String(200), doc="content")

    time = db.Column(db.DateTime, doc="创建时间")


class Checklist(db.Model):
    __tablename__ = 'checklist'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="checklist_id")
    username = db.Column(db.String(32), doc="username")
    checklist = db.Column(db.String(4000000), doc="checklist")
    remark = db.Column(db.String(100), doc="备注")

    time = db.Column(db.DateTime, doc="创建时间")


class HealthAid(db.Model):
    __tablename__ = 'health_aid'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="checklist_id")
    username = db.Column(db.String(32), doc="username")
    title = db.Column(db.String(100), doc="标题")
    abstract = db.Column(db.String(100), doc="概要")
    diya = db.Column(db.String(20), doc="血压（低压）")
    gaoya = db.Column(db.String(20), doc="血压（高压）")
    xuetang = db.Column(db.String(20), doc="血糖")
    xuezhi = db.Column(db.String(20), doc="血脂")
    content = db.Column(db.String(200), doc="正文")

    time = db.Column(db.DateTime, doc="创建时间")


class FriendRequest(db.Model):
    __tablename__ = 'friend_request'

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, doc="关系id")

    username_1 = db.Column(db.String(32), doc="用户1")
    username_2 = db.Column(db.String(32), doc="用户2")
    remark = db.Column(db.String(100), doc="备注")

    time = db.Column(db.DateTime, doc="创建时间")


class StarBlog(db.Model):
    __tablename__ = 'star_blog'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    blog_id = db.Column(db.Integer)


class UserLoggedIn(db.Model):
    __tablename__ = 'user_logged_in'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(32), doc="用户")

    time = db.Column(db.DateTime, doc="过期时间")
