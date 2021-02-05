#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户中心模块
包含用户、权限、角色模块的编辑、添加、删除、列表接口
"""

# 导入正则,格式校验
import re
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app
# 导入自定义的状态码
from deliver.utils.response_code import RET
# 导入模型类
from deliver.models import Role, User, Auth
# 导入数据库实例
from deliver import db
# 导入登陆验证码装饰器
from deliver.utils.commons import login_required
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 添加用户
@api.route('/user/add', methods=['POST'])
@login_required
def user_add():
    """
    创建新用户
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')

    # 进一步获取详细的参数信息
    account = user_data.get('account').encode("UTF-8")
    name = user_data.get('name').encode("UTF-8")
    mobile = user_data.get('mobile').encode("UTF-8")
    wxid = user_data.get('wxid').encode("UTF-8")
    mail = user_data.get('mail').encode("UTF-8")
    pwd = user_data.get('pwd').encode("UTF-8")
    role_id = user_data.get('role_id')

    # 校验参数手机号和密码的完整性
    if not all([account, name, mobile, wxid, mail, pwd, role_id]):
        return jsonify(code=RET.PARAMERR, errmsg='参数缺失')
    # 校验账号
    if not re.match(r'^[A-Za-z]{1}[A-Za-z0-9_-]{3,15}$', account):
        return jsonify(code=RET.DATAERR, errmsg='账号格式错误')
    # 校验姓名
    if not type(name) == str:
        return jsonify(code=RET.DATAERR, errmsg='姓名格式错误')
    # 校验手机号
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(code=RET.DATAERR, errmsg='手机号格式错误')
    # 校验邮箱
    if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}', mail):
        return jsonify(code=RET.DATAERR, errmsg='邮箱格式错误')
    # 校验微信号
    if not re.match(r'^[a-zA-Z\d_]{5,}$', wxid):
        return jsonify(code=RET.DATAERR, errmsg='微信号格式错误')
    # 校验角色格式
    if not type(role_id) == int:
        return jsonify(code=RET.DATAERR, errmsg='角色格式错误')
    # 校验角色是否存在
    try:
        role = Role.query.filter_by(id=role_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取用户信息异常')
    else:
        if not role:
            return jsonify(code=RET.DATAEXIST, errmsg='角色不存在')
    # 校验用户名是否已注册
    try:
        user = User.query.filter_by(account=account).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取用户信息异常')
    else:
        if user:
            return jsonify(code=RET.DATAEXIST, errmsg='用户名已注册')
    # 写入日志
    current_app.logger.info("添加用户:account=%s, name=%s, mobile=%s, mail=%s, wxid=%s, role_id=%s" % (account, name,
           mobile, mail, wxid, role_id))
    # 存储用户信息，使用模型类存储用户注册信息
    user = User(account=account, name=name, mobile=mobile, mail=mail, wxid=wxid, role_id=role_id, state=1)
    # 通过user.password调用了generate_password_hash方法，实现密码的加密存储
    user.password = pwd  # 密码加密
    try:
        # 调用数据库会话对象，用来保存用户注册信息，提交数据到mysql数据库中
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(code=RET.DBERR, errmsg='保存用户信息异常')

    # 返回结果
    return jsonify(code=RET.OK, errmsg='新增用户成功')


# 添加角色
@api.route('/role/add', methods=['POST'])
@login_required
def role_add():
    """
    创建新角色
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    role_data = request.get_json()
    if not role_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')

    # 进一步获取详细的参数信息
    name = role_data.get('name').encode("UTF-8")
    auths = role_data.get('auths')
    # 校验参数
    if not all([name, auths]):
        return jsonify(code=RET.PARAMERR, errmsg='参数缺失')
    # 校验角色名格式
    if not type(name) == str:
        return jsonify(code=RET.DATAERR, errmsg='角色名格式错误')
    # 校验角色权限格式
    if not type(auths) == list:
        return jsonify(code=RET.DATAERR, errmsg='角色权限格式错误')
    # 校验角色权限是否存在
    try:
        auth_list = [v.id for v in Auth.query.all()]
        print "auth_list", auth_list, type(auth_list)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取权限信息异常')
    if set(auth_list) < set(auths):
        return jsonify(code=RET.DATAERR, errmsg='角色权限错误')
    # 校验角色名是否已注册
    try:
        role = Role.query.filter_by(name=name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取角色信息异常')
    else:
        if role:
            return jsonify(code=RET.DATAEXIST, errmsg='角色名已注册')
    # 写入日志
    current_app.logger.info("添加角色:name=%s, auths=%s" % (name, auths))
    # 存储用户信息，使用模型类存储角色信息
    role = Role(
        name=name,
        auths=",".join(map(lambda v: str(v), auths))
    )
    try:
        db.session.add(role)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(code=RET.DBERR, errmsg='保存角色信息异常')

    # 返回结果
    return jsonify(code=RET.OK, errmsg='新增角色成功')


# 删除角色
@api.route('/role/del', methods=['POST'])
@login_required
def role_del():
    """
    删除角色
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    role_data = request.get_json()
    if not role_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')

    pass

    # 返回结果
    return jsonify(code=RET.OK, errmsg='删除角色成功')


# 角色列表
@api.route('/role/list/<int:page>', methods=['GET'])
@login_required
def role_list(page=None):
    """
    删除角色
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    if page is None:
        page = 1
    try:
        role = Role.query.paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取权限信息异常')

    data = [v.to_dict() for v in role.items]
    # 返回结果
    return jsonify(code=RET.OK, errmsg='成功', data=data)


# 角色编辑
@api.route('/role/edit', methods=['POST'])
@login_required
def role_edit():
    """
    删除角色
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    role_data = request.get_json()
    if not role_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')

    pass

    # 返回结果
    return jsonify(code=RET.OK, errmsg='删除角色成功')


# 添加权限
@api.route('/auth/add', methods=['POST'])
@login_required
def auth_add():
    """
    创建新权限
    1/获取参数，name，url
    2/校验参数存在，进一步获取详细参数信息
    3/校验姓名格式
    4/判断用户是否已经注册
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    auth_data = request.get_json()

    if not auth_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    name = auth_data.get('name').encode("UTF-8")
    url = auth_data.get('url').encode("UTF-8")

    # 校验参数
    if not all([name, url]):
        return jsonify(code=RET.PARAMERR, errmsg='参数缺失')
    # 校验权限名
    if not type(name) == str:
        return jsonify(code=RET.DATAERR, errmsg='权限名格式错误')
    # 校验权限规则
    if not type(url) == str:
        return jsonify(code=RET.DATAERR, errmsg='权限规则格式错误')
    # 校验权限名是否已注册
    try:
        auth = Auth.query.filter_by(auth_name=name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取用户信息异常')
    else:
        if auth:
            return jsonify(code=RET.DATAEXIST, errmsg='权限名已注册')

    # 写入日志
    current_app.logger.info("添加权限：name=%s, url=%s" % (name, url))
    # 存储用户信息，使用模型类存储权限信息
    auth = Auth(auth_name=name, url=url)
    try:
        db.session.add(auth)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(code=RET.DBERR, errmsg='保存权限信息异常')

    # 返回结果
    return jsonify(code=RET.OK, errmsg='新增权限成功')


# 权限列表
@api.route('/auth/list/<int:page>', methods=['GET'])
@login_required
def auth_list(page=None):
    """
    查询权限列表
    1/获取参数页面：page，
    2/查询权限列表数据
    3/组装为数据字典
    4/返回响应数据
    :return:
    """
    if page is None:
        page = 1
    try:
        auth = Auth.query.paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, errmsg='获取权限信息异常')

    data = [v.auth_to_dict() for v in auth.items]
    # 返回结果
    return jsonify(code=RET.OK, errmsg='成功', data=data)


# 权限删除
@api.route('/auth/del', methods=['POST'])
@login_required
def auth_del():
    """
    权限删除

    """
    auth_data = request.get_json()
    if not auth_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    auth_id = auth_data.get('auth_id')
    if not all([auth_id]):
        return jsonify(code=RET.PARAMERR, errmsg='参数缺失')
    if not int == type(auth_id):
        return jsonify(code=RET.PARAMERR, errmsg='参数类型错误')

    pass


# 权限编辑
@api.route('/auth/edit', methods=['POST'])
@login_required
def auth_edit():
    """
    权限编辑

    """

    auth_data = request.get_json()
    if not auth_data:
        return jsonify(code=RET.PARAMERR, errmsg='参数错误')
    auth_id = auth_data.get("id").encode("UTF-8")
    auth_name = auth_data.get("name").encode("UTF-8")

    data = Auth.query.get_or_404(auth_id)

    role.auths = ",".join(map(lambda v: str(v), data.get('auths')))
    db.session.add(role)
    db.session.commit()
    return jsonify(code=RET.PARAMERR, errmsg='权限编辑成功')
    pass
