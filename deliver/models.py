# -*- coding:utf-8 -*-

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    account = db.Column(db.String(32), unique=True, nullable=False)  # 账号
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    name = db.Column(db.String(32), unique=True, nullable=False)  # 招聘名称
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    wxid = db.Column(db.String(32), unique=True, nullable=False)  # 微信号
    mail = db.Column(db.String(100), unique=True)  # 邮箱
    state = db.Column(db.Integer, nullable=False)  # 账号状态 0 为停用 1为启用
    weeks = db.relationship("WeekData", backref="user")  # 用户周数据
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)  # 角色外键
    resume_id = db.relationship("Resume", backref='user')

    @property
    def password(self):
        """获取password属性时被调用"""
        raise AttributeError("不可读")

    @password.setter
    def password(self, passwd):
        """设置password属性时被调用，设置密码加密"""
        self.password_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        """检查密码的正确性"""
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "user_id": self.id,
            "account": self.account,
            "name": self.name,
            "mobile": self.mobile,
            "wx": self.wxid,
            "mail": self.mail,
            # "avatar": constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """将实名信息转换为字典数据"""
        auth_dict = {
            "user_id": self.id,
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return auth_dict


# 用户周数据
class WeekData(BaseModel, db.Model):
    """招聘周数据"""

    __tablename__ = "hr_week_data"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    rec = db.Column(db.Integer)  # 推荐人数
    filter_success = db.Column(db.Integer)  # 筛选通过人数
    interview = db.Column(db.Integer)  # 面试人数
    offer = db.Column(db.Integer)  # 面试通过人数
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 周数据用户的编号

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            # "user_id": self.id,
            "rec": self.rec,
            "filter_success": self.filter_success,
            "interview": self.interview,
            "offer": self.offer,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return user_dict


# 角色
class Role(BaseModel, db.Model):
    """角色"""

    __tablename__ = 'role'
    # 定义用户角色表在数据库中的名称

    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(128), unique=True)  # 角色名称
    auths = db.Column(db.String(512))  # 权限列表 数组
    admins = db.relationship("User", backref='role')  # 用户外键关系关联

    def to_dict(self):
        """将角色信息转换为字典数据"""

        auth_dict = {
            "role_id": self.id,
            "rolel_name": self.name,
            "auths": self.auths
        }
        return auth_dict


# 权限
class Auth(BaseModel, db.Model):
    """角色"""

    __tablename__ = 'auth'
    # 定义角色权限表在数据库中的名称
    id = db.Column(db.Integer, primary_key=True)  # 编号
    auth_name = db.Column(db.String(100), unique=True)  # 权限名称
    url = db.Column(db.String(255), unique=True)  # 路由

    def __init__(self, auth_name, url):

        self.auth_name = auth_name
        self.url = url

    def __repr__(self):

        return '<Auth %r>' % self.auth_name

    def auth_to_dict(self):
        """将权限信息转换为字典数据"""
        auth_dict = {
            "auth_id": self.id,
            "auth_name": self.auth_name,
            "url": self.url
        }
        return auth_dict


class Test(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True)

    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):

        self.username = username

        self.email = email

    def __repr__(self):

        return '<User %r>' % self.username


# 简历
class Resume(BaseModel, db.Model):
    """简历"""

    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(32), nullable=False)  # 候选人姓名
    sex = db.Column(db.Enum("男", "女"))  # 性别
    age = db.Column(db.Integer)  # 年龄
    uuid = db.Column(db.String(20), unique=True, nullable=False)  # 身份证号
    phone = db.Column(db.String(11), unique=True, nullable=False)  # 手机号码
    email = db.Column(db.String(100), unique=True, nullable=False)  # 邮箱
    education = db.Column(db.String(11))  # 学历
    exp = db.Column(db.String(11))  # 工作经验
    wish_money = db.Column(db.String(11))  # 期望薪资
    evaluate = db.Column(db.String(100))  # 推荐评语
    file = db.relationship("ResumeFile", backref='resume')  # 附件
    state = db.Column(db.Integer, nullable=False)  # 简历状态
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 所属招聘

    def resume_to_dict(self):
        """将简历信息转换为字典数据"""
        resume_dict = {
            "id": self.id,
            "name": self.name,
            "sex": self.sex,
            "age": self.age,
            "uuid": self.uuid,
            "phone": self.phone,
            "email": self.email,
            "education": self.education,
            "exp": self.exp,
            "wish_money": self.wish_money,
            "evaluate": self.evaluate,
            "state": self.state
        }
        return resume_dict


class ResumeFile(BaseModel, db.Model):
    """简历附件"""
    __tablename__ = 'resume_file'

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("resume.id"), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    fileName = db.Column(db.String(20), nullable=False)


"""
简历关联表
创建简历的时候生成条记录用于简历列表使用 同时 每次推荐生成简历日志表 记录推荐日志

"""
# if __name__ == '__main__':
    # 1
    # db.create_all()

    # 2
    # recruiter = Recruiter(name="胡珊")
    # db.session.add(recruiter)
    # db.session.commit()

    # 2.1
    # auth = Auth(name="添加权限", url="authadd")
    # db.session.add(auth)
    # db.session.commit()

    # 3.插入一条管理员数据
    # from werkzeug.security import generate_password_hash  # 导入生成密码的工具
    # # #
    # admin = Admin(
    #     name="admin",
    #     pwd=generate_password_hash("123456"),
    #     is_super=0,
    #     role_id=1
    # )
    # # # 导入
    # db.session.add(admin)
    # # # 提交
    # db.session.commit()