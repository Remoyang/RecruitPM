#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公共事物处理中心

"""
# 导入正则,实现手机号格式校验
import re
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app, session, g
# 导入自定义的状态码
from deliver.utils.response_code import RET
# 导入模型类
from deliver.models import User
# 导入登陆验证码装饰器
from deliver.utils.commons import login_required
# 导入数据库实例
from deliver import db


@api.route('/sessions', methods=['POST'])
def login():
    """
    登陆
    1/获取参数，username，password，get_json()
    2/校验参数存在，进一步获取详细参数信息
    3/校验手机号格式，re
    4/查询数据库，验证用户信息存在，
    5/校验查询结果，检查密码正确
    6/缓存用户信息
    7/返回前端，user_id
    :return:
    """
    # 获取参数，mobile,password,args,data,form,method,url,
    user_data = request.get_json()
    print "user_data", user_data
    # 校验参数存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 进一步获取详细的参数信息
    username = user_data.get('username').encode("UTF-8")
    password = user_data.get('password')
    # 校验参数用户名和密码的完整性
    if not all([username, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 校验用户名
    if not type(username) == str:
        return jsonify(errno=RET.DATAERR, errmsg='用户名格式错误')
    # 查询数据库，确认用户信息的存在，获取到密码信息
    try:
        user = User.query.filter_by(account=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息异常')
    # 校验查询结果，以及判断密码是否正确
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 缓存用户信息
    session['user_id'] = user.id
    session['name'] = username
    # session['mobile'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='登录成功', data={'user_id': user.id})


@api.route('/session', methods=['DELETE'])
@login_required
def logout():
    """
    退出登陆
    1/清除缓存的用户信息
    :return:
    """
    session.clear()
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/session', methods=['GET'])
def check_login():
    """检查登陆状态"""
    # 尝试从session中获取用户的名字
    name = session.get('name')
    # 如果session中的name存在，则表示已经登陆，否则未登录
    if name:
        return jsonify(errno=RET.OK, errmsg='true', data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')