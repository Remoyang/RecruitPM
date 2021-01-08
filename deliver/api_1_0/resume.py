#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简历处理模块

"""
# 导入时间模块
from datetime import datetime
# 导入正则
import re
# 导入蓝图
from . import api
# 导入flask内置的方法
from flask import request, jsonify, current_app, g
# 导入自定义的状态码
from deliver.utils.response_code import RET
# 导入模型类
from deliver.models import Resume, ResumeFile, ProjectJoinResume, ResumeLog, Project
# 导入数据库实例
from deliver import db, constant
# 导入登陆验证码装饰器
from deliver.utils.commons import login_required
# 导入云存储上传模块
from deliver.utils.file_storage import storage

import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 添加简历
@api.route('/resume/add', methods=['POST'])
@login_required
def resume():
    """
    创建新简历
    1/获取参数，account，name，mobile，wxid， mail，pwd
    2/校验参数存在，进一步获取详细参数信息
    3/校验账号格式，手机号格式，姓名格式，邮箱格式，微信号格式，re
    4/判断候选人是否已经存在
    5/存储简历信息,需求关联信息,简历日志,提交数据
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
    self_evaluation = user_data.get('self_evaluation').encode("UTF-8")  # 自我评价
    job_exp = user_data.get('job_exp').encode("UTF-8")  # 工作经验
    recruit_exp = user_data.get('recruit_exp').encode("UTF-8")  # 项目经验
    file_id = user_data.get('file_id')  # 附件ID

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
    # 校验自我评价
    if not type(self_evaluation) == str:
        return jsonify(errno=RET.DATAERR, errmsg='自我评价格式错误')
    # 校验工作经验
    if not type(job_exp) == str:
        return jsonify(errno=RET.DATAERR, errmsg='工作经验格式错误')
    # 校验项目经验
    if not type(recruit_exp) == str:
        return jsonify(errno=RET.DATAERR, errmsg='项目经验格式错误')

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

    # 简历信息
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
        user_id=user_id,
        self_evaluation=self_evaluation,
        job_exp=job_exp,
        recruit_exp=recruit_exp,
    )

    # 简历日志表
    resume_log = ResumeLog(
        info="创建简历成功"
    )

    try:
        db.session.add(resume)
        db.session.flush()
        resume_id = resume.id
        db.session.add(resume_log)
        db.session.flush()
        resumelog_id = resume_log.id
        # 简历关联需求表
        rroject_join_resume = ProjectJoinResume(
            resume_id=resume_id,
            project_id="",
            project_name="",
            push_time="",
            adopt_time="",
            resumelog=resumelog_id
        )

        db.session.add(rroject_join_resume)

        # 判断是否有附件
        if file_id:
            ResumeFile.query.filter_by(id=file_id).update({"resume_id": resume_id})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存角色信息异常')

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='新增简历成功')


# 简历列表
@api.route('/resume/list/<int:page>', methods=['GET'])
@login_required
def resume_list(page=None):
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
@api.route('/resume/show/<int:rid>', methods=['GET'])
@login_required
def resume_show(rid=None):
    """
    获取简历信息接口
    1/校验参数
    2/查询简历详情数据
    3/组装为数据字典
    4/返回响应数据
    :param rid:
    :return:
    """
    if rid is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        resume = Resume.query.filter_by(id=int(rid)).first()
        resume_file = ResumeFile.query.filter_by(resume_id=int(rid)).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取简历详情信息异常')

    data = resume.resume_to_dict()
    resume_file_data = resume_file.ResumeFile_to_dict()
    data["file_url"] = resume_file_data["url"]
    data["fileName"] = resume_file_data["fileName"]

    return jsonify(errno=RET.OK, errmsg='成功', data=data)
 

# 简历上传
@api.route('/resume/uploadFiles', methods=['POST'])
@login_required
def resume_uploadFiles():
    up_file = request.files.get('file')  # 上传的文件

    if up_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='附件未上传')
    # 提取文件信息
    file_name = up_file.filename
    file_data = up_file.read()

    # 调用云存储上传附件
    try:
        file_key = storage(file_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='附件上传失败')


    resume_file = ResumeFile(
        url=constant.QINIU_DOMIN_PREFIX + file_key,
        fileName=file_name,
        fileKey=file_key
    )

    try:
        db.session.add(resume_file)
        db.session.flush()
        resume_file_id = resume_file.id
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储附件信息异常')

    data = {
        "db": resume_file_id,
        # "deleteUrl": constant.QINIU_DOMIN_PREFIX + file_key,
        "file_name": file_key,
        "msg": "",
        "name": file_name,
        # "size": "4.66 MB",·
        # "type": "application/pdf"
    }

    return jsonify(errno=RET.OK, errmsg='上传简历成功', data=data)


# 简历编辑
@api.route('/resume/edit/<int:page>', methods=['POST', 'GET'])
@login_required
def resume_edit(rid=None):
    pass


# 需求添加
@api.route('/project/add', methods=['POST'])
@login_required
def project_add():
    """
    创建新项目需求
    1/获取参数，job_name, Job_type, level, other, lead, audition_site, education, exp, entry_time, offer, hc, project_name,
             job_feature, job_duty, city, office_site, hc_type, urgent_level, info
    2/校验参数存在，进一步获取详细参数信息
    5/存储需求信息,提交数据
    6/返回响应数据
    :return:
    """

    user_data = request.get_json()

    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 进一步获取详细的参数信息
    user_id = g.user_id
    job_name = user_data.get('job_name').encode("UTF-8")  # 岗位名称
    Job_type = user_data.get('Job_type').encode("UTF-8")  # 岗位类型
    level = user_data.get('level').encode("UTF-8")  # 级
    other = user_data.get('other').encode("UTF-8")  # 别
    lead = user_data.get('lead').encode("UTF-8")  # 面试官
    audition_site = user_data.get('audition_site').encode("UTF-8")  # 面试地点
    education = user_data.get('education').encode("UTF-8")  # 学历要求
    exp = user_data.get('exp').encode("UTF-8")  # 工作经验
    entry_time = user_data.get('entry_time').encode("UTF-8")  # 期望到岗时间
    offer = user_data.get('offer').encode("UTF-8")  # 报价
    hc = user_data.get('hc').encode("UTF-8")  # hc
    project_name = user_data.get('project_name').encode("UTF-8")  # 项目名称
    job_feature = user_data.get('job_feature').encode("UTF-8")  # JD
    job_duty = user_data.get('job_duty').encode("UTF-8")  # 工作职责
    city = user_data.get('city').encode("UTF-8")  # 城市
    office_site = user_data.get('office_site').encode("UTF-8")  # 办公地点
    hc_type = user_data.get('hc_type').encode("UTF-8")  # hc类型
    urgent_level = user_data.get('urgent_level').encode("UTF-8")  # 紧急程度
    info = user_data.get('info').encode("UTF-8")  # 备注信息

    # 校验必填参数
    if not all(
            [job_name, Job_type, level, other, lead, audition_site, education, exp, entry_time, offer, hc, project_name,
             job_feature, job_duty, city, office_site, hc_type, urgent_level, info]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 校验岗位名称
    if not type(job_name) == str:
        return jsonify(errno=RET.DATAERR, errmsg='岗位名称格式错误')
    # 校验岗位类型
    if not type(Job_type) == str:
        return jsonify(errno=RET.DATAERR, errmsg='岗位类型格式错误')
    # 校验级
    if not type(level) == str:
        return jsonify(errno=RET.DATAERR, errmsg='级格式错误')
    # 校验别
    if not type(other) == str:
        return jsonify(errno=RET.DATAERR, errmsg='别格式错误')
    # 校验面试官
    if not type(lead) == str:
        return jsonify(errno=RET.DATAERR, errmsg='面试官格式错误')
    # 校验面试地点
    if not type(audition_site) == str:
        return jsonify(errno=RET.DATAERR, errmsg='面试地点格式错误')
    # 校验学历要求
    if not type(education) == str:
        return jsonify(errno=RET.DATAERR, errmsg='学历要求格式错误')
    # 校验工作经验
    if not isinstance(exp, str):
        return jsonify(errno=RET.DATAERR, errmsg='工作经验格式错误')
    # 校验期望到岗时间
    if not isinstance(entry_time, str):
        return jsonify(errno=RET.DATAERR, errmsg='期望到岗时间格式错误')
    # 校验报价
    if not isinstance(offer, str):
        return jsonify(errno=RET.DATAERR, errmsg='报价格式错误')
    # 校验岗位数
    if not isinstance(hc, str):
        return jsonify(errno=RET.DATAERR, errmsg='岗位数格式错误')
    # 校验项目名称
    if not isinstance(project_name, str):
        return jsonify(errno=RET.DATAERR, errmsg='项目名称格式错误')
    # 校验JD
    if not isinstance(job_feature, str):
        return jsonify(errno=RET.DATAERR, errmsg='JD格式错误')
    # 校验工作职责
    if not isinstance(job_duty, str):
        return jsonify(errno=RET.DATAERR, errmsg='工作职责格式错误')
    # 校验城市
    if not isinstance(city, str):
        return jsonify(errno=RET.DATAERR, errmsg='城市格式错误')
    # 校验办公地点
    if not isinstance(office_site, str):
        return jsonify(errno=RET.DATAERR, errmsg='办公地点格式错误')
    # 校验hc类型
    if not isinstance(hc_type, str):
        return jsonify(errno=RET.DATAERR, errmsg='hc类型格式错误')
    # 校验紧急程度
    if not isinstance(urgent_level, str):
        return jsonify(errno=RET.DATAERR, errmsg='紧急程度格式错误')
    # 校验备注信息
    if not isinstance(info, str):
        return jsonify(errno=RET.DATAERR, errmsg='备注信息格式错误')

    project_id = "tem-" + datetime.now().strftime('%Y-%m-%d-0%S')

    # 需求信息
    project = Project(
        project_id=project_id,
        job_name=job_name,
        Job_type=Job_type,
        level=level,
        other=other,
        lead=lead,
        audition_site=audition_site,
        exp=exp,
        entry_time=entry_time,
        offer=offer,
        hc=hc,
        project_name=project_name,
        job_feature=job_feature,
        job_duty=job_duty,
        city=city,
        office_site=office_site,
        hc_type=hc_type,
        urgent_level=urgent_level,
        info=info,
        )

    try:
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果存储数据发生异常，需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存需求信息异常')

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='新增需求成功')


# 需求列表
@api.route('/project/list/<int:page>', methods=['GET'])
@login_required
def project_list(page=None):
    """
    :param page:
    查询项目需求列表
    1/获取参数页面：page，
    2/查询项目需求列表数据
    3/组装为数据字典
    4/返回响应数据
    :return:
    """
    if page is None:
        page = 1

    try:
        project = Project.query.paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取权限信息异常')

    data = [v.project_to_dict() for v in project.items]

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='成功', data=data)


# 需求详情
@api.route('/project/show/<int:pid>', methods=['GET'])
@login_required
def project_show(pid=None):
    """
        获取简历信息接口
        1/校验参数
        2/查询简历详情数据
        3/组装为数据字典
        4/返回响应数据
        :param pid:
        :return:
        """
    if pid is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        project = Project.query.filter_by(id=int(pid)).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取简历详情信息异常')

    data = project.project_to_dict()

    return jsonify(errno=RET.OK, errmsg='成功', data=data)


# 需求编辑
@api.route('/project/edit', methods=['POST', 'GET'])
@login_required
def project_edit():
    pass
