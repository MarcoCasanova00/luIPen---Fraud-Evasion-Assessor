import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024

    GEOIP_DB_PATH = os.environ.get('GEOIP_DB_PATH', 'GeoLite2-City.mmdb')
    MODEL_PATH = os.environ.get('MODEL_PATH', 'fraud_model.pkl')
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), MODEL_PATH)

    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day"

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    VERSION = '1.0.0'
    PROJECT_NAME = 'Fraud Evasion Penetration Testing Tool'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV = 'production'


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}