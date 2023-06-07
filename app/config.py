# -*- coding: utf-8 -*-
"""
Flask 配置文件
"""


class Config(object):
    """
    通用配置
    """
    SECRET_KEY = 'woluanxiede'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    """
    开发模式配置
    """
    TYPE = 'dev'
    DEBUG = True

    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USERNAME = '1160708111'
    MAIL_PASSWORD = 'wjaotbnncizagcgg'

    SQLALCHEMY_DATABASE_URI = "sqlite:///be-patient-develop.db"

    JWT_KEY = '123456'


class ProductionConfig(Config):
    """
    生产模式配置
    """
    TYPE = 'prod'

    DEBUG = False
    # ENV = 'production'

    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USERNAME = '1160708111'
    MAIL_PASSWORD = 'wjaotbnncizagcgg'

    SQLALCHEMY_DATABASE_URI = "sqlite:///be-patient.db"

    JWT_KEY = '123456'


class TestConfig(Config):
    """
    测试模式配置
    """
    TYPE = 'test'
    DEBUG = True

    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USERNAME = '1160708111'
    MAIL_PASSWORD = 'wjaotbnncizagcgg'

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

    SERVER_NAME = "localhost:5000"

    JWT_KEY = '123456'


configs = {
    "default": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "test": TestConfig
}
