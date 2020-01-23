import os
from os.path import abspath, dirname

from dotenv import load_dotenv
from utils.collect import collect_filter


class BaseConfig:
    def __init__(self):
        self.BASE_DIR = abspath(dirname(__file__))
        self.CURRENT_ENV = os.environ.get('CURRENT_ENV', 'dev')
        self.LOCAL_MODE = bool(int(os.environ.get('LOCAL_MODE', 1)))
        self.LOCAL_HOST = '127.0.0.1'

        self.LOGGER_LEVEL = 'INFO'

        # flask
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = os.environ['FLASK_SECRET_KEY']

        # flask-wtf
        self.WTF_CSRF_ENABLED = True
        self.WTF_CSRF_SECRET_KEY = os.environ['WTF_CSRF_SECRET_KEY']

        # flask-mail
        self.MAIL_DEBUG = False
        self.MAIL_SERVER = os.environ['MAIL_SERVER']
        self.MAIL_PORT = os.environ['MAIL_PORT']
        self.MAIL_USE_TLS = False
        self.MAIL_USE_SSL = True
        self.MAIL_USERNAME = os.environ['MAIL_USERNAME']
        self.MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
        self.MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
        self.MAIL_MAX_EMAILS = None
        self.MAIL_ASCII_ATTACHMENTS = False

        # db
        self.DB_HOST = 'postgres'
        self.DB_PORT = '5432'
        self.DB_USER = os.environ['POSTGRES_USER']
        self.DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
        self.DB_NAME = os.environ['POSTGRES_DB']

        # rabbitmq
        self.RABBITMQ_HOST = 'rabbitmq'
        self.RABBITMQ_PORT = 5672
        self.RABBITMQ_USER = os.environ['RABBITMQ_DEFAULT_USER']
        self.RABBITMQ_PASSWORD = os.environ['RABBITMQ_DEFAULT_PASS']

        # itsdangerous
        self.ACTIVATION_SALT = os.environ['ACTIVATION_SALT']

        # flask-collect
        self.COLLECT_EXCLUDED_BLUEPRINTS = ('swagger_ui',)
        self.COLLECT_STORAGE = 'flask_collect.storage.file'
        self.COLLECT_FILTER = lambda blueprints: collect_filter(
            blueprints, self.COLLECT_EXCLUDED_BLUEPRINTS
        )

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class DevConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.LOGGER_LEVEL = 'DEBUG'

        # flask
        self.DEBUG = True
        self.TESTING = True

        # flask-mail
        self.MAIL_DEBUG = True

        # rabbitmq
        self.RABBITMQ_HOST = (
            self.LOCAL_HOST if self.LOCAL_MODE else self.RABBITMQ_HOST
        )

        # db
        self.DB_HOST = self.LOCAL_HOST if self.LOCAL_MODE else self.DB_HOST


class TestConfig(DevConfig):
    def __init__(self):
        super().__init__()

        self.LOGGER_LEVEL = 'INFO'

        # flask-wtf
        self.WTF_CSRF_ENABLED = False

        # db
        self.DB_NAME = f'test_{self.DB_NAME}'


class ProdConfig(BaseConfig):
    def __init__(self):
        super().__init__()


config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}


def _get_config_gen():
    load_dotenv()
    conf = config[os.environ.get('CURRENT_ENV', 'dev')]()
    while True:
        yield conf


_config_gen = _get_config_gen()
next(_config_gen)


def get_config():
    return next(_config_gen)
