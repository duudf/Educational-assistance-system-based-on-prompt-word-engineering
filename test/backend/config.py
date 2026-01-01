# 配置文件

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 用于加密 JWT Token，务必修改成一个复杂的随机字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY') or 'sk-gnzqqqhchjmeetbwagsvecjoapqmgigufkdbusuyoopazxkn'