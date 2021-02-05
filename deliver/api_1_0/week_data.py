#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据处理中心

"""
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify
# 导入自定义的状态码
from deliver.utils.response_code import RET
# 导入模型类
# from app.models import WeekData


@api.route('/sessions', methods=['POST'])
def hrweek():
    """招聘每周数据"""

    week_data = {'user_id': WeekData.id}
    return jsonify(code=RET.OK, errmsg='OK', data=week_data)