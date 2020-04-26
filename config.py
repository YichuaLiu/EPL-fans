import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
    # 保密性
    SECRET_KEY = os.environ.get('SECRET_KEY') or db['secret_key']
    # 验证码
    # RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or db['recaptcha_public_key']
    # RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or db['recaptcha_private_key']
    # print(RECAPTCHA_PUBLIC_KEY)
    # print(RECAPTCHA_PRIVATE_KEY)
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or db['site_key']
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or db['in_key']

    # 数据库设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or db['mysql_path']
    # 存储到环境变量
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('GMAIL_USERNAME') or db['email']
    MAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD') or db['password']
