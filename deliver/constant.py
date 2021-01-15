# -*- coding:utf-8 -*-

# 图片验证码Redis有效期， 单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码Redis有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 七牛空间域名
QINIU_DOMIN_PREFIX = "http://ouwyn64sa.bkt.clouddn.com/"

# 七牛命名空间
QINIU_SPACE_NAME = 'csig'

# 城区信息redis缓存时间，单位：秒
# AREA_INFO_REDIS_EXPIRES = 7200

# 首页展示最多的房屋数量
# HOME_PAGE_MAX_HOUSES = 5

# 首页房屋数据的Redis缓存时间，单位：秒
# HOME_PAGE_DATA_REDIS_EXPIRES = 7200

# 房屋详情页展示的评论最大数
# HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# 房屋详情页面数据Redis缓存时间，单位：秒
# HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200

# 房屋列表页面每页显示条目数
# HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页面Redis缓存时间，单位：秒
# HOUSE_LIST_REDIS_EXPIRES = 7200

JSON_AS_ASCII = False

# 简历状态字字典
RESUME_STATE = {
    "0": "新简历",
    "1": "简历初筛选不通过",
    "2": "待筛选",
    "3": "预约面试",
    "4": "面试确认",
    "5": "改约中",
    "6": "面试中",
    "7": "待发offer",
    "9": "offer确认",
    "10": "人员入场",
    "11": "等待到岗",
    "12": "结束",
    "13": "简历筛选不通过",
    "14": "放弃面试",
    "15": "面试不通过",
    "16": "放弃offer",
    "17": "放弃到岗",
    "18": "关闭岗位",
    "19": "到岗",
    "20": "离职"
}

# 项目状态
PROJECT_STATE = {
    "0": "关闭",
    "1": "招聘中"
}

# 紧急程度
URGENT_LEVEL = {
    "0": "",
    "1": "加急",
    "2": "高",
    "3": "正常",
    "4": "暂缓",
    "5": "关闭"
}

HC_TYPE = {
    "0": "新增",
    "1": "替补"
}


# 登陆错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

# 登陆错误限制的时间，单位：秒
LOGIN_ERROR_FORBID_TIME = 600
