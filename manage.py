#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 项目启动文件
from deliver import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 应用程序实例，指定开发者模式
app = create_app("development")
# 创建数据库表
manage = Manager(app)
Migrate(app, db)
manage.add_command("db", MigrateCommand)


if __name__ == '__main__':
    print app.url_map
    # app.run()
    manage.run()
