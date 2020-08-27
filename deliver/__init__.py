# -*- coding:utf-8 -*-
import logging
import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config_map, Config
from utils.commons import RegexConverter
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 实现csrf保护
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志的保存路径，每个日志文件的最大大小，保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                等级      输入日志信息的文件名    行数       日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（current_app）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 创建应用程序实例
# 工厂模式
def create_app(config_name):
    """
     创建flask的应用对象
     :param config_name:  str  配置模式的名字  （"develop", "product"）
     :return: app
    """

    app = Flask(__name__)
    # 从配置对象中为app设置配置信息
    app.config.from_object(config_map[config_name])
    # 正则url
    app.url_map.converters["regex"] = RegexConverter
    # 添加csrf保护，类似于设置form.csrf_token()
    # csrf.init_app(app)
    # app.config['JSON_AS_ASCII'] = False

    # 利用flask-session，将session数据保存到redis中
    Session(app)

    # 使用app初始化db
    db.init_app(app)

    # 使用蓝图
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")
    from deliver import web_html

    app.register_blueprint(web_html.html)
    # from .web_page import html as html_blueprint
    # app.register_blueprint(html_blueprint)

    return app
