#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简历处理模块

"""
# 导入时间模块
import datetime
# 导入正则
import re
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app, g
# 导入自定义的状态码
from deliver.utils.response_code import RET
# 导入模型类
from deliver.models import Resume, ResumeFile
# 导入数据库实例
from deliver import db
# 导入登陆验证码装饰器
from deliver.utils.commons import login_required
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 添加简历
@api.route('/resunme/add', methods=['POST'])
@login_required
def resunme_add():
    """
    创建新简历
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断候选人是否已经存在
    5/存储用户注册信息,提交数据
    6/返回响应数据
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 进一步获取详细的参数信息
    user_id = g.user_id
    name = user_data.get('name').encode("UTF-8")  # 姓名
    uuid = user_data.get('uuid').encode("UTF-8")  # 身份证号
    phone = user_data.get('phone').encode("UTF-8")  # 手机号码
    wxid = user_data.get('wxid').encode("UTF-8")
    email = user_data.get('email').encode("UTF-8")  # 邮箱
    education = user_data.get('education').encode("UTF-8")  # 学历
    exp = user_data.get('exp').encode("UTF-8")   # 工作经验
    wish_money = user_data.get('wish_money').encode("UTF-8")  # 期望薪资
    evaluate = user_data.get('evaluate').encode("UTF-8")  # 推荐评语

    # 校验必填参数
    if not all(
            [name, uuid, phone, wxid, email, education, exp, wish_money, evaluate]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 校验姓名
    if not type(name) == str:
        return jsonify(errno=RET.DATAERR, errmsg='姓名格式错误')
    # 校验身份证
    if not re.match(r'^\d{6}(18|19|20)?\d{2}(0[1-9]|1[012])(0[1-9]|[12]\d|3[01])\d{3}(\d|X)$', uuid):
        return jsonify(errno=RET.DATAERR, errmsg='身份证号格式错误')
    # 校验手机号
    if not re.match(r'^1[34578]\d{9}$', phone):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    # 校验邮箱
    if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}', email):
        return jsonify(errno=RET.DATAERR, errmsg='邮箱格式错误')
    # 校验微信号
    if not re.match(r'^[a-zA-Z\d_]{5,}$', wxid):
        return jsonify(errno=RET.DATAERR, errmsg='微信号格式错误')
    # 校验学历
    if not type(education) == str:
        return jsonify(errno=RET.DATAERR, errmsg='学历格式错误')
    # 校验工作经验
    if not type(exp) == str:
        return jsonify(errno=RET.DATAERR, errmsg='工作经验格式错误')
    # 校验期望薪资
    if not type(wish_money) == str:
        return jsonify(errno=RET.DATAERR, errmsg='期望薪资格式错误')
    # 校验推荐评语
    if not type(evaluate) == str:
        return jsonify(errno=RET.DATAERR, errmsg='推荐评语格式错误')

    # 校验身份证是否已注册
    try:
        role = Resume.query.filter_by(uuid=uuid).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取候选人信息异常')
    else:
        if role:
            return jsonify(errno=RET.DATAEXIST, errmsg='候选人已存在')

    # 根据身份证判断性别
    if (int(uuid[16:17]) % 2) == 0:
        sex = '女'
    else:
        sex = '男'

    # 根据身份证计算年龄
    birth = uuid[6:14]
    barth_day = datetime.datetime.strptime(birth, "%Y%m%d")
    now = datetime.datetime.now()
    days = (now - barth_day).days
    age = days // 365

    resume = Resume(
        name=name,
        sex=sex,
        age=age,
        uuid=uuid,
        phone=phone,
        email=email,
        education=education,
        exp=exp,
        wish_money=wish_money,
        evaluate=evaluate,
        state=0,
        user_id=user_id
    )
    try:
        db.session.add(resume)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存角色信息异常')

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='新增简历成功')


# 简历列表
@api.route('/resunme/list/<int:page>', methods=['POST'])
def resunme_list(page=None):
    """
    :param page:
    查询简历列表
    1/获取参数页面：page，
    2/查询简历列表数据
    3/组装为数据字典
    4/返回响应数据
    :return:
    """
    if page is None:
        page = 1
    try:
        resume = Resume.query.paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取权限信息异常')

    data = [v.resume_to_dict() for v in resume.items]
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='成功', data=data)


# 简历详情
@api.route('/resunme/show/<int:id>', methods=['GET'])
def resunme_show(id=None):
    """
    获取简历信息接口
    1/校验参数
    2/查询简历详情数据
    3/组装为数据字典
    4/返回响应数据
    :param id:
    :return:
    """
    if id is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        resume = Resume.query.paginate(id, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取权限信息异常')

    data = [v.resume_to_dict() for v in resume.items]

    return jsonify(errno=RET.OK, errmsg='成功', data=data)