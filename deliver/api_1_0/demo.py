# !/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入蓝图对象
from . import api
from deliver.models import Test
from deliver import db


@api.route("/demo")
def index():
    print 123
    data = Test(username="test", email="test1")
    db.session.add(data)
    db.session.commit()

    return "index page"