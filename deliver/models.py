# -*- coding:utf-8 -*-
# 导入时间模块
from datetime import datetime
# 导入加密模块
from werkzeug.security import generate_password_hash, check_password_hash
# 导入配置
from constant import RESUME_STATE, PROJECT_STATE, URGENT_LEVEL, HC_TYPE
from deliver import db
# from . import db
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

        role_dict = {
            "role_id": self.id,
            "role_name": self.name,
            "auths": self.auths
        }
        return role_dict


# 权限
class Auth(BaseModel, db.Model):
    """权限"""

    __tablename__ = 'auth'
    # 定义角色权限表在数据库中的名称
    id = db.Column(db.Integer, primary_key=True)  # 编号
    auth_name = db.Column(db.String(100), unique=True)  # 权限名称
    url = db.Column(db.String(255), unique=True)  # 路由

    # def __init__(self, auth_name, url):
    #
    #     self.auth_name = auth_name
    #     self.url = url

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


# 简历
class Resume(BaseModel, db.Model):
    """简历"""

    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(32), nullable=False)  # 候选人姓名
    sex = db.Column(db.String(2))  # 性别
    age = db.Column(db.Integer)  # 年龄
    uuid = db.Column(db.String(20), unique=True, nullable=False)  # 身份证号
    phone = db.Column(db.String(11), unique=True, nullable=False)  # 手机号码
    email = db.Column(db.String(100), unique=True, nullable=False)  # 邮箱
    education = db.Column(db.String(11))  # 学历
    exp = db.Column(db.String(11))  # 工作年限
    wish_money = db.Column(db.String(11))  # 期望薪资
    self_evaluation = db.Column(db.TEXT)  # 自我评价
    job_exp = db.Column(db.TEXT)  # 工作经验
    recruit_exp = db.Column(db.TEXT)  # 项目经验
    evaluate = db.Column(db.TEXT)  # 推荐评语
    file = db.relationship("ResumeFile", backref='resume')  # 附件
    state = db.Column(db.Integer, nullable=False)  # 简历状态
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 所属招聘
    project_join = db.relationship("ProjectJoinResume", backref='resume')   # 需求关联表

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
            "self_evaluation": self.self_evaluation,
            "job_exp": self.job_exp,
            "recruit_exp": self.recruit_exp,
            "state": RESUME_STATE[str(self.state)]
        }

        return resume_dict

    def resume_name_to_dict(self):
        resume_name_dict = {
            "id": self.id,
            "name": self.name,
        }

        return resume_name_dict


class ResumeFile(BaseModel, db.Model):
    """简历附件"""
    __tablename__ = 'resume_file'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resume.id"))
    url = db.Column(db.String(256), nullable=False)
    fileName = db.Column(db.String(128), nullable=False)
    fileKey = db.Column(db.String(128), nullable=False)

    def ResumeFile_to_dict(self):
        """将简历附件信息转换为字典数据"""

        ResumeFile_dict = {
            "id": self.id,
            "resume_id": self.resume_id,
            "url": self.url,
            "fileName": self.fileName,
            "fileKey": self.fileKey,
        }
        return ResumeFile_dict


class ProjectJoinResume(BaseModel, db.Model):
    """
    简历关联表
    创建简历的时候生成条记录用于简历列表使用 同时 每次推荐生成简历日志表 记录推荐日志

    """
    __tablename__ = 'project_join_resume'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resume.id"), nullable=False)
    resume_name = db.Column(db.String(11))  # 候选人名称
    resume_state = db.Column(db.Integer, nullable=False)  # 简历状态
    project_id = db.Column(db.String(11))  # 推荐的项目岗位ID
    project_number = db.Column(db.String(20))  # 需求编号
    project_name = db.Column(db.String(11))  # 推荐的项目岗位名称
    push_time = db.Column(db.DateTime)  # 推荐面试时间
    adopt_time = db.Column(db.DateTime)  # 面试通过时间
    resumelog = db.Column(db.Integer, db.ForeignKey("resume_log.id"), nullable=False)  # 流水日志ID

    def ProjectJoinResume_to_dicr(self):

        push_time = self.form_date(self.push_time)
        adopt_time = self.form_date(self.adopt_time)
        if not self.project_number:
            project_number = ""
        else:
            project_number = self.project_number

        ProjectJoinResume_dicr = {
            "id": self.id,
            "resume_id": self.resume_id,
            "resume_name": self.resume_name,
            "resume_state": RESUME_STATE[str(self.resume_state)],
            "project_id": self.project_id,
            "project_number": project_number,
            "project_name": self.project_name,
            "push_time": push_time,
            "adopt_time": adopt_time,
            "resumelog": self.resumelog
        }

        return ProjectJoinResume_dicr

    def form_date(self, data):
        """格式化时间格式"""
        if type(data) == unicode:
            data = ''
        elif not data:
            data = ''
        else:
            data = data.strftime("%Y-%m-%d %H:%M:%S")
        return data


class ResumeLog(BaseModel, db.Model):
    """简历日志流水表"""

    __tablename__ = 'resume_log'

    id = db.Column(db.Integer, primary_key=True)
    project_join = db.relationship("ProjectJoinResume", backref='resume_log')  # 需求关联表
    info = db.Column(db.TEXT)  # 日志信息

    def resumelog_to_dice(self):

        resumelog_dict = {
            "id": self.id,
            "project_join": self.project_join,
            "info": self.info
        }

        return resumelog_dict


class Project(BaseModel, db.Model):
    """项目需求表"""

    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)  # 项目岗位ID
    project_id = db.Column(db.String(20), nullable=False)  # 项目岗位编号
    job_name = db.Column(db.String(32), nullable=False)  # 岗位名称
    Job_type = db.Column(db.String(32), nullable=False)  # 岗位类型
    level = db.Column(db.String(32), nullable=False)  # 级
    other = db.Column(db.String(32), nullable=False)  # 别
    lead = db.Column(db.String(32), nullable=False)  # 面试官
    audition_site = db.Column(db.String(32), nullable=False)  # 面试地点
    education = db.Column(db.String(11))  # 学历要求
    exp = db.Column(db.String(11))  # 工作经验
    entry_time = db.Column(db.DateTime)  # 期望到岗时间
    offer = db.Column(db.String(32), nullable=False)  # 报价
    hc = db.Column(db.Integer, nullable=False)  # hc
    pushnum = db.Column(db.Integer, nullable=False)  # 推荐简历数
    project_name = db.Column(db.String(32), nullable=False)  # 项目名称
    job_feature = db.Column(db.TEXT, nullable=False)  # JD
    job_duty = db.Column(db.TEXT, nullable=False)  # 工作职责
    city = db.Column(db.String(32), nullable=False)  # 城市
    office_site = db.Column(db.String(32))  # 办公地点
    hc_type = db.Column(db.String(32), nullable=False)  # hc类型
    urgent_level = db.Column(db.String(32), nullable=False)  # 紧急程度
    info = db.Column(db.TEXT)   # 备注
    state = db.Column(db.Integer, nullable=False)  # 需求状态 0 为停用 1为启用

    def project_to_dict(self):
        project_dict = {
            "id": self.id,
            "project_id": self.project_id,
            "job_name": self.job_name,
            "Job_type": self.Job_type,
            "level": self.level,
            "other": self.other,
            "lead": self.lead,
            "audition_site": self.audition_site,
            "education": self.education,
            "exp": self.exp,
            "entry_time": self.entry_time.strftime('%Y-%m-%d'),
            "offer": self.offer,
            "hc": self.hc,
            "pushnum": self.pushnum,
            "project_name": self.project_name,
            "job_feature": self.job_feature,
            "job_duty": self.job_duty,
            "city": self.city,
            "office_site": self.office_site,
            "hc_type": HC_TYPE[str(self.hc_type)],
            "urgent_level": URGENT_LEVEL[str(self.urgent_level)],
            "info": self.info,
            "create_time": self.create_time.strftime('%Y-%m-%d'),
            "state": PROJECT_STATE[str(self.state)]
        }

        return project_dict


# if __name__ == '__main__':
    # 1
    # db.create_all()

    # 2
    # recruiter = Recruiter(name="胡珊")
    # db.session.add(recruiter)
    # db.session.commit()

    # 2.1
    # role = Role(name="管理员", auths="[]")
    # auth = Auth(auth_name="添加权限", url="/user/add")
    # db.session.add(role)
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