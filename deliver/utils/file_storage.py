# -*- coding: utf-8 -*-

# 附件对象存储

# flake8: noqa

from qiniu import Auth, put_data, etag
# import qiniu.config
# 导入云存储的配置
from config import Config
from deliver.constant import QINIU_SPACE_NAME
# 需要填写你的 Access Key 和 Secret Key
# access_key = '4eOgmvL43X8npfQyhuTzcJtxsst8wqUNWxerfnp7'
# secret_key = 'm04OhFkWEiBpdhu-uwmPQw2t0mbc2vAi9u6sxHub'


def storage(file_data):
    """
    上传文件到七牛服务器
    :param file_data: 要上传的文件数据
    :return:
    """

    # 构建鉴权对象
    q = Auth(Config.access_key, Config.secret_key)

    # 要上传的空间
    bucket_name =QINIU_SPACE_NAME

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)

    # 测试
    # print(info)
    # print('*' * 10)
    # print(ret)

    # 生产
    if info.status_code == 200:
        # 上传成功,返回图片的名字key
        return ret.get('key')
    else:
        # 上传失败，抛出异常
        raise Exception('上传七牛失败')


if __name__ == '__main__':
    with open(u'./简历.pdf', 'rb') as f:
        file_data = f.read()
        storage(file_data)